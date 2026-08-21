import os
import io
import json
import zipfile
import asyncio
import requests
from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title='GhostReel Explorer')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

SESSION_FILE = os.path.join(BASE_DIR, 'session.json')
NICHES_FILE = os.path.join(BASE_DIR, 'niches.json')
RADAR_CACHE_FILE = os.path.join(BASE_DIR, 'radar_cache.json')

def load_saved_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def load_niches():
    if os.path.exists(NICHES_FILE):
        try:
            with open(NICHES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_niches(data):
    with open(NICHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_radar_cache():
    if os.path.exists(RADAR_CACHE_FILE):
        try:
            with open(RADAR_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_radar_cache(data):
    with open(RADAR_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_session_data(sid: str, username: str = None, user_id: str = None):
    data = {'sessionid': sid, 'username': username, 'user_id': user_id}
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    return data

def get_direct_video_url(shortcode: str, cached_vurl: str = None) -> str:
    # 1. Se URL do CDN foi fornecida e ainda responde OK
    if cached_vurl:
        try:
            r = requests.head(cached_vurl, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            if r.status_code == 200:
                return cached_vurl
        except Exception:
            pass

    # 2. Busca URL atualizada via API Mobile
    try:
        sess = load_saved_session()
        headers = {
            'User-Agent': 'Instagram 319.0.0.38.109 Android',
            'X-IG-App-ID': '936619743392459',
        }
        cookies = {'sessionid': sess.get('sessionid'), 'ds_user_id': sess.get('user_id')} if sess.get('sessionid') else {}
        r_info = requests.get(f'https://i.instagram.com/api/v1/media/{shortcode}/info/', headers=headers, cookies=cookies, timeout=8)
        if r_info.status_code == 200:
            items = r_info.json().get('items', [])
            if items and items[0].get('video_versions'):
                return items[0]['video_versions'][0].get('url')
    except Exception:
        pass
    return None

class DownloadItem(BaseModel):
    shortcode: str
    video_url: str = None
    url: str = None

class DownloadRequest(BaseModel):
    items: list[DownloadItem]

class SessionRequest(BaseModel):
    sessionid: str

@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name='index.html')

@app.get('/api/proxy_image')
def proxy_image(url: str):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=8)
        return Response(content=r.content, media_type=r.headers.get('Content-Type', 'image/jpeg'))
    except Exception:
        return Response(status_code=404)

@app.get('/api/session/status')
def get_session_status():
    sess = load_saved_session()
    if sess.get('sessionid'):
        return {'logged_in': True, 'username': sess.get('username', 'conectado')}
    return {'logged_in': False}

class NicheCreateRequest(BaseModel):
    name: str
    seeds: list[str]

@app.get('/api/niches')
def get_niches():
    return load_niches()

@app.post('/api/niches')
def create_niche(req: NicheCreateRequest):
    niches = load_niches()
    n_id = req.name.lower().replace(' ', '_')
    new_niche = {"id": n_id, "name": req.name.upper(), "seeds": req.seeds}
    niches.append(new_niche)
    save_niches(niches)
    return {"status": "success", "niche": new_niche}


@app.post('/api/session')
async def save_session(req: SessionRequest):
    try:
        sid = req.sessionid.strip()
        user_id = sid.split('%3A')[0] if '%3A' in sid else sid.split(':')[0]
        
        headers = {
            'User-Agent': 'Instagram 319.0.0.38.109 Android (33/13; 420dpi; 1080x2400; samsung; SM-G998B; p3s; exynos2100; en_US)',
            'X-IG-App-ID': '936619743392459',
        }
        cookies = {'sessionid': sid, 'ds_user_id': user_id}
        r = requests.get(f'https://i.instagram.com/api/v1/users/{user_id}/info/', headers=headers, cookies=cookies, timeout=10)
        
        username = 'conectado'
        if r.status_code == 200:
            username = r.json().get('user', {}).get('username', username)
            
        save_session_data(sid, username, user_id)
        return {'status': 'success', 'username': username, 'message': f'Conta @{username} conectada com sucesso!'}
    except Exception as e:
        return JSONResponse(status_code=400, content={'error': str(e)})

@app.get('/api/scrape/stream')
async def scrape_stream(username: str, limit: int = 12, media_type: str = 'reels'):
    async def event_generator():
        try:
            sess = load_saved_session()
            sid = sess.get('sessionid')
            user_id_cookie = sess.get('user_id') or (sid.split('%3A')[0] if sid and '%3A' in sid else '')

            headers = {
                'User-Agent': 'Instagram 319.0.0.38.109 Android (33/13; 420dpi; 1080x2400; samsung; SM-G998B; p3s; exynos2100; en_US)',
                'X-IG-App-ID': '936619743392459',
            }
            cookies = {}
            if sid:
                cookies['sessionid'] = sid
                cookies['ds_user_id'] = user_id_cookie

            s = requests.Session()
            s.headers.update(headers)
            s.cookies.update(cookies)

            # 1. Obter perfil
            r_user = s.get(f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}', headers={'X-IG-App-ID': '936619743392459', 'User-Agent': 'Mozilla/5.0'}, timeout=8)
            
            target_user_id = None
            profile_data = {}
            
            if r_user.status_code == 200:
                u = r_user.json().get('data', {}).get('user', {})
                target_user_id = u.get('id')
                
                related = []
                try:
                    r_chain = s.get(f'https://i.instagram.com/api/v1/discover/chaining/?target_id={target_user_id}', timeout=5)
                    if r_chain.status_code == 200:
                        for item in r_chain.json().get('users', [])[:20]:
                            if item.get('username'):
                                related.append({
                                    'username': item.get('username'),
                                    'full_name': item.get('full_name', ''),
                                    'profile_pic_url': item.get('profile_pic_url', '')
                                })
                except Exception as ex:
                    print(f"Error fetching chaining: {ex}")
                
                profile_data = {
                    'username': u.get('username', username),
                    'full_name': u.get('full_name', ''),
                    'biography': u.get('biography', ''),
                    'followers': u.get('edge_followed_by', {}).get('count', 0),
                    'following': u.get('edge_follow', {}).get('count', 0),
                    'profile_pic_url': u.get('profile_pic_url', ''),
                    'total_posts': u.get('edge_owner_to_timeline_media', {}).get('count', 0),
                    'related_profiles': related
                }
            else:
                r_lookup = s.get(f'https://i.instagram.com/api/v1/users/lookup/?q={username}', timeout=8)
                if r_lookup.status_code == 200:
                    u = r_lookup.json().get('user', {})
                    target_user_id = str(u.get('pk'))
                    profile_data = {
                        'username': u.get('username', username),
                        'full_name': u.get('full_name', ''),
                        'biography': '',
                        'followers': u.get('follower_count', 0),
                        'following': 0,
                        'profile_pic_url': u.get('profile_pic_url', ''),
                        'total_posts': 0,
                        'related_profiles': []
                    }
                else:
                    raise Exception(f'Perfil @{username} não encontrado ou privado.')

            yield f"data: {json.dumps({'type': 'profile', 'profile': profile_data})}\n\n"
            await asyncio.sleep(0.01)

            # 2. Extrair Posts / Reels via API Mobile Ultra-Rápida
            count = 0
            max_id = None
            has_more = True

            while count < limit and has_more:
                items = []
                
                if media_type == 'reels':
                    payload = {'target_user_id': str(target_user_id), 'page_size': str(min(limit - count, 20))}
                    if max_id:
                        payload['max_id'] = str(max_id)
                    r_clips = s.post('https://i.instagram.com/api/v1/clips/user/', data=payload, timeout=10)
                    if r_clips.status_code == 200:
                        res = r_clips.json()
                        items = [c.get('media', {}) for c in res.get('items', [])]
                        max_id = res.get('paging_info', {}).get('max_id')
                        has_more = res.get('paging_info', {}).get('more_available', False)
                else:
                    url = f'https://i.instagram.com/api/v1/feed/user/{target_user_id}/'
                    if max_id:
                        url += f'?max_id={max_id}'
                    r_feed = s.get(url, timeout=10)
                    if r_feed.status_code == 200:
                        res = r_feed.json()
                        items = res.get('items', [])
                        max_id = res.get('next_max_id')
                        has_more = res.get('more_available', False)

                if not items:
                    break

                batch = []
                for item in items:
                    if count >= limit:
                        break

                    is_video = (item.get('media_type') == 2) or bool(item.get('video_versions'))
                    is_sidecar = (item.get('media_type') == 8) or ('carousel_media' in item)

                    if media_type == 'reels' and not is_video:
                        continue
                    elif media_type == 'carousels' and not is_sidecar:
                        continue

                    shortcode = item.get('code')
                    views = item.get('play_count') or item.get('view_count') or 0
                    likes = item.get('like_count') or 0
                    comments = item.get('comment_count') or 0
                    duration = item.get('video_duration') or 0

                    caption_text = ''
                    if item.get('caption') and isinstance(item.get('caption'), dict):
                        caption_text = item['caption'].get('text', '')
                    if caption_text and len(caption_text) > 120:
                        caption_text = caption_text[:120] + '...'

                    thumb_url = ''
                    if item.get('image_versions2', {}).get('candidates'):
                        thumb_url = item['image_versions2']['candidates'][0].get('url', '')
                    
                    video_url = None
                    if item.get('video_versions') and len(item['video_versions']) > 0:
                        video_url = item['video_versions'][0].get('url')

                    type_label = 'REEL' if is_video else ('CARROSSEL' if is_sidecar else 'FOTO')

                    batch.append({
                        'shortcode': shortcode,
                        'url': f'https://instagram.com/reel/{shortcode}/' if is_video else f'https://instagram.com/p/{shortcode}/',
                        'video_url': video_url,
                        'thumbnail_url': thumb_url,
                        'views': views,
                        'likes': likes,
                        'comments': comments,
                        'duration': duration,
                        'caption': caption_text,
                        'timestamp': item.get('taken_at', 0),
                        'is_video': is_video,
                        'is_sidecar': is_sidecar,
                        'type_label': type_label
                    })
                    count += 1

                if batch:
                    yield f"data: {json.dumps({'type': 'reels_batch', 'reels': batch})}\n\n"
                    await asyncio.sleep(0.01)

            yield f"data: {json.dumps({'type': 'done', 'count': count})}\n\n"

        except Exception as e:
            err_raw = str(e)
            yield f"data: {json.dumps({'type': 'error', 'error': err_raw, 'raw_error': err_raw})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get('/api/radar/stream')
async def radar_stream(seed: str = Query(..., description="Username semente ou ID do nicho"), depth: int = 15):
    async def event_generator():
        try:
            sess = load_saved_session()
            sid = sess.get('sessionid')
            user_id_cookie = sess.get('user_id') or (sid.split('%3A')[0] if sid and '%3A' in sid else '')

            headers = {
                'User-Agent': 'Instagram 319.0.0.38.109 Android (33/13; 420dpi; 1080x2400; samsung; SM-G998B; p3s; exynos2100; en_US)',
                'X-IG-App-ID': '936619743392459',
            }
            cookies = {}
            if sid:
                cookies['sessionid'] = sid
                cookies['ds_user_id'] = user_id_cookie

            s = requests.Session()
            s.headers.update(headers)
            s.cookies.update(cookies)

            # Verificar se seed é um ID de nicho preset
            niches = load_niches()
            target_seeds = [seed]
            for n in niches:
                if n['id'] == seed or n['name'].lower() == seed.lower():
                    target_seeds = n['seeds']
                    break

            visited_users = set()
            queue = list(target_seeds)

            processed_count = 0

            while queue and processed_count < depth:
                current_username = queue.pop(0).strip().lstrip('@')
                if not current_username or current_username in visited_users:
                    continue
                visited_users.add(current_username)

                yield f"data: {json.dumps({'type': 'status', 'message': f'Analisando @{current_username}...'})}\n\n"
                await asyncio.sleep(0.01)

                try:
                    # 1. Obter info do perfil
                    r_user = s.get(f'https://i.instagram.com/api/v1/users/web_profile_info/?username={current_username}', headers={'X-IG-App-ID': '936619743392459', 'User-Agent': 'Mozilla/5.0'}, timeout=6)
                    
                    target_user_id = None
                    followers = 0
                    full_name = ''
                    bio = ''
                    pic_url = ''
                    total_posts = 0

                    if r_user.status_code == 200:
                        u = r_user.json().get('data', {}).get('user', {})
                        target_user_id = u.get('id')
                        followers = u.get('edge_followed_by', {}).get('count', 0)
                        full_name = u.get('full_name', '')
                        bio = u.get('biography', '')
                        pic_url = u.get('profile_pic_url', '')
                        total_posts = u.get('edge_owner_to_timeline_media', {}).get('count', 0)
                    else:
                        r_lookup = s.get(f'https://i.instagram.com/api/v1/users/lookup/?q={current_username}', timeout=6)
                        if r_lookup.status_code == 200:
                            u = r_lookup.json().get('user', {})
                            target_user_id = str(u.get('pk'))
                            followers = u.get('follower_count', 0)
                            full_name = u.get('full_name', '')
                            pic_url = u.get('profile_pic_url', '')
                        else:
                            continue

                    if not target_user_id:
                        continue

                    # 2. Descobrir mais contas do mesmo nicho via chaining (alimenta a corrente)
                    try:
                        r_chain = s.get(f'https://i.instagram.com/api/v1/discover/chaining/?target_id={target_user_id}', timeout=5)
                        if r_chain.status_code == 200:
                            for item in r_chain.json().get('users', []):
                                un = item.get('username')
                                if un and un not in visited_users and un not in queue:
                                    queue.append(un)
                    except Exception:
                        pass

                    # 3. Puxar últimos 12 vídeos para identificar os Top 3 Virais
                    r_clips = s.post('https://i.instagram.com/api/v1/clips/user/', data={'target_user_id': str(target_user_id), 'page_size': '15'}, timeout=8)
                    reels_list = []
                    if r_clips.status_code == 200:
                        raw_items = [c.get('media', {}) for c in r_clips.json().get('items', [])]
                        for item in raw_items:
                            if item.get('media_type') == 2 or item.get('video_versions'):
                                sc = item.get('code')
                                v_views = item.get('play_count') or item.get('view_count') or 0
                                v_likes = item.get('like_count') or 0
                                v_url = item['video_versions'][0].get('url') if item.get('video_versions') else None
                                t_url = item.get('image_versions2', {}).get('candidates', [{}])[0].get('url', '')
                                dur = item.get('video_duration', 0)
                                cap = item.get('caption', {}).get('text', '') if isinstance(item.get('caption'), dict) else ''
                                reels_list.append({
                                    'shortcode': sc,
                                    'views': v_views,
                                    'likes': v_likes,
                                    'video_url': v_url,
                                    'thumbnail_url': t_url,
                                    'duration': dur,
                                    'caption': cap[:90] + '...' if len(cap) > 90 else cap
                                })

                    # Ordenar vídeos por views e selecionar Top 3
                    reels_list.sort(key=lambda x: x['views'], reverse=True)
                    top_3_virals = reels_list[:3]

                    max_views = top_3_virals[0]['views'] if top_3_virals else 0
                    outlier_score = round(max_views / max(followers, 1), 2)

                    profile_entry = {
                        'username': current_username,
                        'full_name': full_name,
                        'biography': bio,
                        'profile_pic_url': pic_url,
                        'followers': followers,
                        'total_posts': total_posts,
                        'max_views': max_views,
                        'outlier_score': outlier_score,
                        'top_virals': top_3_virals
                    }

                    processed_count += 1
                    yield f"data: {json.dumps({'type': 'profile_found', 'profile': profile_entry})}\n\n"
                    await asyncio.sleep(0.02)

                except Exception as ex:
                    print(f"Erro analisando {current_username}: {ex}")
                    continue

            yield f"data: {json.dumps({'type': 'done', 'count': processed_count})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Download individual direto para o navegador com salvamento local
@app.get('/api/download_video/{shortcode}')
def download_single_video(shortcode: str, vurl: str = None):
    target_path = os.path.join(DOWNLOAD_DIR, f"{shortcode}.mp4")
    
    # 1. Se ja tiver no disco local, entrega direto
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
        return FileResponse(target_path, filename=f"{shortcode}.mp4", media_type="video/mp4")

    # 2. Obtem URL de video
    video_url = get_direct_video_url(shortcode, vurl)
    if not video_url:
        return JSONResponse(status_code=404, content={'error': 'URL do vídeo indisponível.'})

    try:
        r = requests.get(video_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True, timeout=30)
        if r.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(r.content)
            return FileResponse(target_path, filename=f"{shortcode}.mp4", media_type="video/mp4")
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})

# Download em lote empacotado em .ZIP direto para o navegador
@app.post('/api/download_zip')
async def download_zip(req: DownloadRequest):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for item in req.items:
            target_path = os.path.join(DOWNLOAD_DIR, f"{item.shortcode}.mp4")
            
            # Se ja existir local
            if not os.path.exists(target_path) or os.path.getsize(target_path) < 1000:
                v_url = get_direct_video_url(item.shortcode, item.video_url)
                if v_url:
                    try:
                        r = requests.get(v_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
                        if r.status_code == 200:
                            with open(target_path, 'wb') as f:
                                f.write(r.content)
                    except Exception:
                        pass
            
            if os.path.exists(target_path):
                zip_file.write(target_path, arcname=f"{item.shortcode}.mp4")

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=ghostreel_batch.zip"}
    )

# Abrir pasta downloads no Windows Explorer
@app.post('/api/open_folder')
def open_downloads_folder():
    try:
        os.startfile(DOWNLOAD_DIR)
        return {'status': 'success', 'message': 'Pasta aberta no Windows Explorer.'}
    except Exception as e:
        return JSONResponse(status_code=500, content={'error': str(e)})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
