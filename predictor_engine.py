import math, hashlib
from football_api import get_recent_form,get_h2h
from cache_store import get_prediction,put_prediction

def poisson(k,lam):return math.exp(-lam)*(lam**k)/math.factorial(k)

def predict_match(home_id,away_id,fixture_id=None):
    key=hashlib.sha256(f'{home_id}:{away_id}:{fixture_id or 0}:v4'.encode()).hexdigest()
    cached=get_prediction(key)
    if cached:return {'success':True,**cached['data'],'prediction_cached':True,'prediction_saved_at':cached['saved_at']}
    hf=get_recent_form(home_id);af=get_recent_form(away_id);hh=get_h2h(home_id,away_id)
    for x in (hf,af,hh):
        if not x.get('success'):return {'success':False,'error':x.get('error','Prediction data unavailable.')}
    h=hf['form'];a=af['form'];head=hh['h2h']; ha=h['goals_per_game'] or 1.15; aa=a['goals_per_game'] or 1.0; hd=h['conceded_per_game'] or 1.1; ad=a['conceded_per_game'] or 1.1
    hx=max(.2,min(3.8,.48*ha+.28*ad+.24*1.05)); ax=max(.15,min(3.5,.48*aa+.28*hd+.24*.9))
    if head['matches']:
        total=(head['home_goals']+head['away_goals'])/head['matches'];hx=.85*hx+.15*max(.1,total*.55);ax=.85*ax+.15*max(.1,total*.45)
    p={'home':0,'draw':0,'away':0}
    for i in range(7):
        for j in range(7):
            v=poisson(i,hx)*poisson(j,ax);p['home' if i>j else 'draw' if i==j else 'away']+=v
    total=sum(p.values()) or 1; hp=round(p['home']/total*100,1);dp=round(p['draw']/total*100,1);ap=round(p['away']/total*100,1);lam=hx+ax
    over15=1-poisson(0,lam)-poisson(1,lam);over25=1-sum(poisson(k,lam) for k in range(3));under25=1-over25;over35=1-sum(poisson(k,lam) for k in range(4));btts=1-math.exp(-hx)-math.exp(-ax)+math.exp(-lam)
    dc1x=hp+dp;dcx2=dp+ap;dc12=hp+ap
    markets={'Home Win':hp,'Draw':dp,'Away Win':ap,'Over 1.5':round(over15*100,1),'Over 2.5':round(over25*100,1),'Under 2.5':round(under25*100,1),'Over 3.5':round(over35*100,1),'BTTS Yes':round(btts*100,1),'BTTS No':round((1-btts)*100,1),'1X':round(dc1x,1),'X2':round(dcx2,1),'12':round(dc12,1)}
    best=max(markets,key=markets.get);conf=round(min(95,max(45,max(hp,dp,ap)*.72+max(0,min(1,(h['matches']+a['matches'])/20))*28)),1);pred='Home Win' if hp>=dp and hp>=ap else ('Away Win' if ap>=hp and ap>=dp else 'Draw')
    ranked=sorted([(i,j,poisson(i,hx)*poisson(j,ax)) for i in range(7) for j in range(7)],key=lambda z:z[2],reverse=True)[:5]
    norm=sum(x[2] for x in ranked) or 1
    correct_score=[{'home_goals':i,'away_goals':j,'probability':round(v/norm*100,1)} for i,j,v in ranked]
    data_quality=round(55+45*min(1,(h['matches']+a['matches'])/20),1)
    reasons=[]
    if h['points_per_game']>a['points_per_game']+.35: reasons.append('Home side has the stronger recent points rate.')
    elif a['points_per_game']>h['points_per_game']+.35: reasons.append('Away side has the stronger recent points rate.')
    if h['goals_per_game']>a['goals_per_game']+.30: reasons.append('Home attack has produced more goals per game recently.')
    if a['conceded_per_game']>h['conceded_per_game']+.30: reasons.append('Away defence has conceded more recently.')
    if head['matches']>=3: reasons.append(f'H2H sample contains {head["matches"]} previous meetings.')
    if not reasons: reasons.append('The model sees a relatively balanced statistical matchup.')
    out={'home_probability':hp,'draw_probability':dp,'away_probability':ap,'predicted_result':pred,'confidence':conf,'home_xg':round(hx,2),'away_xg':round(ax,2),'expected_goals':{'home':round(hx,2),'away':round(ax,2),'total':round(lam,2)},'over_under':{'over_1_5':round(over15*100,1),'over_2_5':round(over25*100,1),'under_2_5':round(under25*100,1),'over_3_5':round(over35*100,1)},'btts':{'yes':round(btts*100,1),'no':round((1-btts)*100,1)},'double_chance':{'1X':round(dc1x,1),'X2':round(dcx2,1),'12':round(dc12,1)},'strongest_market':{'market':best,'probability':markets[best]},'home_form':h,'away_form':a,'h2h':head,'correct_score':correct_score,'data_quality':data_quality,'explanation':reasons,'model_version':'v4','source':'Harmon AI Statistical Engine','prediction_cached':False}
    put_prediction(key,fixture_id or 0,out);return {'success':True,**out}
