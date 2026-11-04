from pathlib import Path
import json, math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).parent
OUT=ROOT/'out'; OUT.mkdir(exist_ok=True)
layout={'status':'draft_requires_user_approval','units':'m','origin':'acute balcony/FIX floor corner','plan_registration':{'origin_px':[24,473],'pixels_per_m':35.2,'status':'approximate_from_previous_9.40m_wall_assumption_not_surveyed'},'items':[
 {'id':'dining','center':[2.9,5.1],'size':[2.40,.99],'angle':70.7},
 {'id':'sofa','center':[5.82,2.50],'size':[2.50,1.07],'angle':90},
 {'id':'tv','center':[9.25,2.50],'size':[1.847,.028],'angle':90,'mount':'wall','brand':'LG','product':'OLED evo AI G6','model':'OLED83G6PJA','diagonal_inches':83,'body_size_m':[1.847,1.057,.028],'dimension_source':'user supplied LG screenshots; stand excluded','mount_offset_status':'mounting bracket and wall stand-off unverified; plan center retained','model_variant':'LG83G6 wall model required; bundled B&O Eclipse65 not suitable'},
 {'id':'speaker_A','center':[9.05,3.75],'size':[.25,.27],'angle':0},
 {'id':'speaker_B','center':[9.05,1.25],'size':[.25,.27],'angle':0}]}
# Trace structural boundaries from the supplied plan; distances remain indicative.
glass=[(24,473),(186,14)]
island=[(159,230),(201,114),(216,120),(194,242)]
def segdist(p,a,b):
 vx,vy=b[0]-a[0],b[1]-a[1]; t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy)))
 return math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy)
def corners(x,y):
 th=math.radians(70.7);c,s=math.cos(th),math.sin(th)
 return [(24+35.2*(x+c*u-s*v),473-35.2*(y+s*u+c*v)) for u,v in [(-1.2,-.495),(1.2,-.495),(1.2,.495),(-1.2,.495)]]
def gaps(x,y):
 p=corners(x,y)
 g=min(segdist(v,*glass) for v in p)/35.2
 k=min([segdist(v,island[j],island[(j+1)%4]) for v in p for j in range(4)]+[segdist(v,p[j],p[(j+1)%4]) for v in island for j in range(4)])/35.2
 return g,k
dx,dy=3.746,5.119
glassgap,kitchengap=gaps(dx,dy)
layout['revision']='F'
sofa=next(item for item in layout['items'] if item['id']=='sofa')
sofa.update({'brand':'Poliform','series':'Ernest','selection_status':'series selected by user','configuration_status':'module combination, actual size, upholstery and colour not selected','size_status':'2.50x1.07m is previous planning placeholder, not verified Ernest product dimensions','placement_status':'retain current TV-facing alignment; recheck footprint after module selection'})
sofa['configuration_brief']={'width_rule':'overall sofa composition including integrated table slightly shorter than recessed TV wall span, not TV screen width','chaise_side':'balcony/window side (lower side of current plan)','opposite_end':'seat plus integrated table arrangement as user reference','reference_image':'C:/Users/akaay/.codex/codex-remote-attachments/01a19f51-138e-7622-817c-433434a14e62/0965C08F-EEEC-4991-B1D2-C022C7AA2E26/1-写真1.jpg','placement_rule':'sofa remains freestanding facing TV; use wall span as width reference','dimensions_status':'recessed wall span and valid module assembly need verification; old 250cm rectangle obsolete','upholstery_reference':'light upholstery in user reference; exact fabric and colour not selected'}
sofa.update({'center':[5.82,2.35],'size':[3.70,1.01],'size_status':'user authorized approximate schematic envelope; not verified manufacturer module assembly','configuration_status':'concept: 3.70m overall including integrated table; window-side chaise approx1.70m depth','recess_span_estimate_m':4.10,'nominal_width_margin_m':.20})
layout['speaker_selection_status']='Confirmed by user: retain B&O Beolab 28 pair; budget change applies to TV only.'
layout['tv_back_wall_finish']={'status':'requested_by_user','material':'natural-toned tile','scope':'TV back wall; exact coverage to verify against joinery','proposed_finish':'matte beige/greige stone look; subtle joints','finish_status':'assistant proposed; exact tile not selected'}
layout['kitchen_audio']={'brand':'Bang & Olufsen','model':'Beosound Balance','quantity':1,'placement':'on kitchen island countertop toward its narrowing tip','position_status':'semantic placement confirmed; exact footprint, countertop height and edge clearance to verify before CG','finish_status':'not selected'}
layout['living_tables']={'status':'user requested provisional pair between sofa and TV','arrangement':'oval coffee table in front of sofa, round side table adjacent along sofa length; precise positions pending footprint verification','items':[{'brand':'BoConcept','series':'Santiago','type':'oval coffee table','finish_reference':'white veined top and natural oak fluted base per user photo','dimensions_status':'not visible in supplied screenshot; verify before assigning coordinates','reference_image':'C:/Users/akaay/.codex/codex-remote-attachments/01a19f51-138e-7622-817c-433434a14e62/96EF8F9F-29F3-49E2-BF1F-5C20881522CC/1-写真1.jpg'},{'brand':'BoConcept','series':'Santiago','type':'round side table','height_m':.51,'diameter_m':.46,'top':'white ceramic','base':'natural oak veneer','dimension_source':'user supplied screenshot','reference_image':'C:/Users/akaay/.codex/codex-remote-attachments/01a19f51-138e-7622-817c-433434a14e62/96EF8F9F-29F3-49E2-BF1F-5C20881522CC/2-写真2.jpg'}]}
for item in layout['items']:
 if item['id'].startswith('speaker_'):
  item.update({'brand':'Bang & Olufsen','model':'Beolab 28','mount':'floor','finish_reference':'user screenshot: brown wooden curtain, silver stem and base; exact finish names unconfirmed','model_source':'bundled official OBJ (not yet downloaded)','footprint_status':'previous provisional footprint; validate against actual base geometry'})
layout['dining_intent']='D position approved; six chairs approved, three per long side.'
layout['items'][0]['center']=[round(dx,2),round(dy,2)]
layout['indicative_clearance_m']={'table_to_glass':round(glassgap,2),'table_to_island':round(kitchengap,2),'method':'shortest plan distances; unverified scale; excludes chairs'}
layout['av_alignment']='TV and sofa share y=2.50; speakers symmetric +/-1.25m; wall zone interpreted from user red rectangle'
layout['table_position_status']='D position approved by user'
layout['chairs']={'count':6,'arrangement':'3 on window side and 3 on opposite side; none at table ends','footprint_status':'indicative 0.50 x 0.55m; product not selected','items':[]}
th=math.radians(70.7);c,s=math.cos(th),math.sin(th)
for side in (-1,1):
 for u in (-.78,0,.78):
  v=side*.77
  layout['chairs']['items'].append({'center':[round(dx+c*u-s*v,3),round(dy+s*u+c*v,3)],'size':[.50,.55],'angle':70.7,'side':'window' if side==1 else 'room'})
layout['living_tables']={'status':'Ernest marble pair proposed by user; layout provisional','brand':'Poliform','series':'Ernest','finish':'marble/travertine; exact stone not selected','source':'https://s3.poliform.it/2025/04/Poliform_catalog_ERNEST_2024.pdf','items':[{'id':'coffee_rect','center':[7.28,3.02],'size':[1.2,.9],'height':.30,'angle':90},{'id':'coffee_square','center':[7.28,1.89],'size':[.9,.9],'height':.30,'angle':90}],'arrangement':'long side parallel to sofa; two tables separated by 0.08m; approximate sofa front clearance 0.475m; replaces Santiago pair and Joan candidate'}
layout['living_tables']['finish']={'base':'black wood / black elm direction','top':'travertino titanium','status':'user proposed mixed material; exact factory combination not yet verified','source':'https://www.poliform.it/en/products/ernest-coffee-table/'}
layout['living_tables']['status']='User corrected selection: 1200x900 plus 1200x700, interlocked like a puzzle per reference'
layout['living_tables']['items'][0]['size']=[1.2,.9]
layout['living_tables']['items'][1]['id']='coffee_rect_700'
layout['living_tables']['items'][1]['size']=[1.2,.7]
layout['living_tables']['arrangement']='Interlocking/notched pair per user image, not two separate rectangles. Exact mating geometry and resulting centres must be obtained from manufacturer model before final placement.'
layout['living_tables']['arrangement_reference']='C:/Users/akaay/.codex/codex-remote-attachments/01a19f51-138e-7622-817c-433434a14e62/C6CF6F88-0177-4234-BD9E-24A9B30F72B3/1-写真1.jpg'
layout['living_tables']['geometry_status']='Current centres and rectangular diagram are legacy placeholders; not the selected interlocking geometry'
layout['living_tables']['finish']={'candidates':[{'base':'black wood','top':'travertino titanium','factory_combination_status':'unverified'},{'base':'dark wood / black elm','top':'dark wood / black elm'}],'status':'not finally selected; user photo specifies arrangement, not red lacquer finish'}
for item in layout['items']:
 if item['id'].startswith('speaker_'):
  item['finish_reference']='dark wood coordinated with Ernest black wood legs; exact Beolab finish to select; metal stem/base unchanged'
  item['finish_status']='dark wood direction requested; exact finish and metal colour not confirmed'
(OUT/'layout_draft.json').write_text(json.dumps(layout,indent=2),encoding='utf-8')
(OUT/'layout_F.json').write_text(json.dumps(layout,indent=2),encoding='utf-8')
im=Image.open(ROOT/'images/plan/floorplan_large.jpg').convert('RGB').resize((1600,1092))
d=ImageDraw.Draw(im,'RGBA'); font=ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',23)
def xy(x,y):return (48+x*70.4,946-y*70.4)
colors=[(184,114,36,150),(43,116,153,150),(62,73,99,190),(62,73,99,210),(62,73,99,210)]
for i,(it,col) in enumerate(zip(layout['items'],colors),1):
 x,y=it['center']; a,b=it['size']; th=math.radians(it['angle']); c,s=math.cos(th),math.sin(th)
 pts=[xy(x+c*u-s*v,y+s*u+c*v) for u,v in [(-a/2,-b/2),(a/2,-b/2),(a/2,b/2),(-a/2,b/2)]]
 d.polygon(pts,fill=col,outline=(20,40,60,255),width=3)
 px,py=xy(x,y); d.ellipse((px-15,py-15,px+15,py+15),fill=(255,255,255,240));d.text((px-8,py-15),str(i),font=font,fill='black')
# Schematic Ernest chaise on window side, and integrated table at kitchen end.
def planbox(x0,y0,x1,y1,fill):
 p0=xy(x0,y1);p1=xy(x1,y0);d.rectangle((*p0,*p1),fill=fill,outline=(35,65,80,255),width=2)
planbox(5.315,.50,7.015,1.40,(73,139,169,210))
planbox(5.315,3.65,5.80,4.20,(58,51,47,230))
for seam in (1.40,2.35,3.30):
 d.line([xy(5.315,seam),xy(6.325,seam)],fill=(35,65,80,255),width=2)
d.line([xy(6.45,2.5),xy(8.5,2.5)],fill=(43,116,153,255),width=4)
for chair in layout['chairs']['items']:
 x,y=chair['center']; a,b=chair['size']
 th=math.radians(chair['angle']); c,s=math.cos(th),math.sin(th)
 pts=[xy(x+c*u-s*v,y+s*u+c*v) for u,v in [(-a/2,-b/2),(a/2,-b/2),(a/2,b/2),(-a/2,b/2)]]
 d.polygon(pts,fill=(184,114,36,100),outline=(85,65,40,255),width=2)
d.polygon([xy(8.5,2.5),xy(8.2,2.62),xy(8.2,2.38)],fill=(43,116,153,255))
# Additional items: symbolic placement only where exact dimensions are unavailable.
for number,it in enumerate(layout['living_tables']['items'],6):
 x,y=it['center'];a,b=it['size'];th=math.radians(it['angle']);c,s=math.cos(th),math.sin(th)
 pts=[xy(x+c*u-s*v,y+s*u+c*v) for u,v in [(-a/2,-b/2),(a/2,-b/2),(a/2,b/2),(-a/2,b/2)]]
 d.polygon(pts,fill=(214,200,176,220),outline=(110,82,48,255),width=3)
 px,py=xy(x,y);d.text((px-9,py-17),str(number),font=font,fill='black')
# Balance symbol on narrowing upper end of kitchen island (not a measured footprint).
d.ellipse((398,240,422,264),fill=(85,105,85,230),outline=(30,60,30,255),width=2)
d.text((430,234),'8',font=font,fill='black')
d.line((714,640,714,930),fill=(175,149,117,220),width=7)
d.rectangle((820,10,1590,290),fill=(255,255,255,245))
lines=['試作CG：Ernestソファ構成・概念案','② 全幅約3.7m／掘り込み約4.1mに対し左右約20cm','窓側カウチ：奥行約1.7m／通常部約1.01m','キッチン側：座面＋一体型テーブル（濃色部分）','寸法・分割線は概念図／正式モジュール未照合','⑥⑦ 120×90＋120×70cm：パズル接合形状は未反映','通路・カウチとテーブルの間隔は要調整']
for j,line in enumerate(lines):d.text((835,18+j*37),line,font=font,fill=(25,40,55,255))
im.save(OUT/'plan_overlay_F.png')
im.crop((120,350,780,930)).save(OUT/'plan_detail_F.png')
im.save(OUT/'plan_latest.png')
im.save(OUT/'plan_ernest.png')
im.crop((120,350,780,930)).save(OUT/'plan_detail_ernest.png')
im.save(OUT/'plan_sofa_concept.png')
im.crop((120,350,780,950)).save(OUT/'plan_sofa_concept_detail.png')
print(json.dumps(layout,ensure_ascii=False,indent=2))
