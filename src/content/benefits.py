import csv, json, collections, re
AK = '/home/claude/ind/dl/acukg/AcuKG/'
FIX = {  # typo / duplicate normalisation of AcuKG indication terms
 'Enteritiris':'Enteritis','Odrsum Of Foot Pain':'Dorsum Of Foot Pain','Odrsum Of Foot Swelling':'Dorsum Of Foot Swelling',
 'Eyelind Twitch':'Eyelid Twitching','Face Puffinesss':'Face Puffiness','Llumbar Pain':'Lumbar Pain',
 'Hypochrondrium Fullness':'Hypochondrium Fullness','Hypochrondrium Pain':'Hypochondrium Pain','External\n Malleolus Pain':'External Malleolus Pain',
 'Color Blindess':'Color Blindness','Foreigh Body Sensation In The Throat':'Foreign Body Sensation In The Throat',
 'Temperomandibular Joint Motor Impairment':'Temporomandibular Joint Motor Impairment','Medical Aspect Of Arm Pain':'Medial Aspect Of Arm Pain',
 'Lower Abdominal Distensiodysuria':'Lower Abdominal Distension','Rectum Prolapse':'Rectal Prolapse','Backache':'Back Pain',
 'Micturition Frequency':'Frequent Urination','Frequent Micturition':'Frequent Urination','Giddiness':'Dizziness','Ophthalmalgia':'Eye Pain',
 'Xerostomia':'Dry Mouth','Vision Blurring':'Blurred Vision','Handache':'Hand Pain','Stomach Pain':'Gastric Pain','Lower Back Pain':'Low Back Pain',
 'Muscle Gastrocnemius Spasm':'Gastrocnemius Spasm','Axillary Region Pain':'Axilla Pain','Axillary Region Swelling':'Axilla Swelling',
 'External Genital Pain':'External Genitalia Pain','Low Abdomen Pain':'Lower Abdominal Pain','Low Abdomen Distension':'Lower Abdominal Distension',
 'Low Abdomen Fullness':'Lower Abdominal Fullness','Profuse Menstruation':'Menorrhagia','Pruritus Vulva':'External Genitalia Pruritus',
 'Morbid Leukorrhea':'Leukorrhea','Low Limb Weakness':'Low Extremity Weakness','Low Limb Numbness':'Low Extremity Numbness',
 'Low Limb Paralysis':'Low Extremity Paralysis','Low Limb Muscular Atrophy':'Low Extremity Muscular Atrophy','Upper Limb Motor Impairment':'Upper Extremity Motor Impairment',
 'Motor Impairment Of Upper Extremity':'Upper Extremity Motor Impairment','Voice Sudden Loss':'Voice Loss','Voice Sudden Hoarseness':'Hoarse Voice',
 'Febrile Diseases Without Sweat':'Febrile Diseases With Anhidrosis','Lumbar Sore':'Lumbar Soreness','Apoplexy-Faint':'Apoplexy',
}
GLOSS = {  # plain-English gloss for medical / TCM terms (shown next to the term)
 'Epistaxis':'nosebleed','Borborygmus':'rumbling stomach','Apoplexy':'stroke','Post-Apoplexy':'after a stroke','Hemiplegia':'one-sided paralysis after stroke',
 'Dysmenorrhea':'painful periods','Amenorrhea':'missed periods','Menorrhagia':'heavy periods','Leukorrhea':'vaginal discharge','Enuresis':'bed-wetting',
 'Dysuria':'painful or difficult urination','Anuria':'no urine output','Hematuria':'blood in urine','Hematemesis':'vomiting blood','Hemoptysis':'coughing blood',
 'Tinnitus':'ringing in the ears','Vertigo':'spinning dizziness','Lacrimation':'watery eyes','Rhinorrhea':'runny nose','Hyposmia':'reduced sense of smell',
 'Tenesmus':'straining with bowel movements','Dysentery':'infectious diarrhoea','Dysphagia':'difficulty swallowing','Aphasia':'loss of speech','Glossoplegia':'paralysis of the tongue',
 'Trismus':'jaw clenching','Lockjaw':'jaw clenching','Erysipelas':'skin infection','Furuncle':'boil','Urticaria':'hives','Scrofula':'neck lymph-node swelling',
 'Goiter':'thyroid swelling','Jaundice':'yellow skin and eyes','Beriberi':'leg weakness and swelling (vitamin B1 deficiency)','Malaria':'malaria (historical use)',
 'Parotitis':'mumps','Mastitis':'breast inflammation','Hernia':'hernia / groin pain','Nocturnal Emission':'night-time ejaculation','Seminal Emission':'involuntary ejaculation',
 'Impotence':'erectile difficulty','Sterility':'infertility','Hypochondrium Pain':'pain under the ribs at the side','Hypochondrium Distension':'bloating under the ribs at the side',
 'Hypochondrium Fullness':'fullness under the ribs at the side','Costal Pain':'rib pain','Costal Fullness':'fullness in the ribs','Epigastric Pain':'pain in the upper stomach area',
 'Gastric Pain':'stomach pain','Febrile Disease':'fever illness','Febrile Diseases With Anhidrosis':'fever without sweating','Afternoon Fever':'low fever in the afternoon',
 'Night Sweat':'sweating at night','Spontaneous Sweat':'sweating without exertion','Palpitation':'awareness of heartbeat','Cardiac Pain':'chest pain over the heart',
 'Mania':'agitation and mania','Hysteria':'emotional outbursts','Dream-Disturbed Sleep':'restless sleep with many dreams','Amnesia':'memory loss',
 'Epilepsy':'seizures','Convulsion':'seizures','Infantile Convulsion':"seizures in children",'Coma':'unconsciousness','Consciousness Loss':'fainting',
 'Heat Stroke':'heat stroke','Common Cold':'cold','Excessive Sputum':'lots of phlegm','Wheezing':'wheezing','Asthma':'asthma / breathlessness',
 'Insufficient Lactation':'low breast-milk supply','Afterbirth Retention':'retained placenta','Prolonged Lochia':'prolonged bleeding after birth',
 'Fetus Malposition':'breech baby','Delayed Labor':'slow labour','Difficult Labor':'difficult labour','Morning Sickness':'pregnancy nausea',
 'Uterus Prolapse':'dropped womb','Rectal Prolapse':'dropped rectum','Hemorrhoids':'piles','Bloody Stool':'blood in stool','Edema':'fluid swelling','General Edema':'swelling all over',
 'Face Paralysis':"facial paralysis (Bell's palsy)",'Mouth Deviation':'crooked mouth after facial paralysis','Eye Deviation':'crooked eye after facial paralysis',
 'Eyelid Ptosis':'drooping eyelid','Night Blindness':'poor vision in dim light','Cornea Cloudiness':'cloudy cornea','Yellowish Sclera':'yellow whites of the eyes',
 'Otorrhea':'ear discharge','Diplacusis':'hearing the same sound at two pitches','Sudden Deafness':'sudden hearing loss','Deafness':'hearing loss',
 'Nasal Obstruction':'blocked nose','Foul Breath':'bad breath','Salivation':'drooling','Decreased Saliva':'dry mouth','Thirst':'thirst',
 'Pulmonary Tuberculosis':'tuberculosis (historical use)','Rabies':'rabies (historical use)','Measles':'measles','Rubella':'rubella',
 'Emaciation Due To General Deficiency':'wasting and weakness','General Body Weakness':'general weakness','Sluggishness':'tiredness',
 'Liver Fire':'TCM: liver fire (irritability, red eyes, headache)','Liver Yang':'TCM: rising liver yang (headache, dizziness)','Interior Wind':'TCM: internal wind (tremor, spasm)',
 'Blood Heat':'TCM: heat in the blood (rashes, bleeding)','Heat':'TCM: heat','Phlegm':'TCM: phlegm','Phlegm Accumulation':'TCM: phlegm accumulation',
 'Heat Excess Arising From The Middle Warmer':'TCM: stomach heat','Fluid Transformation Inadequate':'TCM: poor fluid metabolism','Female Problem':'gynaecological problems',
 'Premenstrual Syndrome':'PMS','Irregular Menstruation':'irregular periods','Uterine Bleeding':'abnormal womb bleeding','Postpartum Hemorrhage':'bleeding after birth',
 'Premature Ejaculation':'premature ejaculation','Vaginitis':'vaginal inflammation','Acid Regurgitation':'acid reflux','Belching':'burping','Hiccup':'hiccups',
 'Anorexia':'poor appetite','Indigestion':'indigestion','Infantile Indigestion':"children's indigestion",'Enteritis':'bowel inflammation','Gastritis':'stomach inflammation',
 'Umbilical Pain':'pain around the navel','Frequent Sneezing':'sneezing','Rosacea':'red nose / rosacea','Eczema':'eczema','General Pruritus':'itching all over',
 'Mute':'inability to speak','Stuttering':'stammer','Hoarse Voice':'hoarseness','Voice Loss':'loss of voice','Sore Throat':'sore throat','Throat Dryness':'dry throat',
 'Foreign Body Sensation In The Throat':'lump-in-the-throat feeling','Obsessive Thought':'obsessive thinking','Mood Instability':'mood swings','Panic':'panic',
 'Manic Depression':'bipolar symptoms','Mental Disorder':'mental disturbance','Dementia':'dementia','Poor Memory':'poor memory','Memory Loss':'memory loss',
 'Sciatica':'sciatica','Lumbar Pain':'lower back pain','Lumbosacral Region Pain':'low back and sacrum pain','Acute Lumbar Sprain':'acute back strain',
 'Nape Pain':'back-of-neck pain','Strained Neck':'stiff neck (wry neck)','Scapular Region Pain':'shoulder-blade pain','Popliteal Fossa Pain':'pain behind the knee',
 'Contracture Of Tendon In Popliteal Fossa':'tight tendons behind the knee','Gastrocnemius Spasm':'calf cramp','External Malleolus Pain':'outer ankle pain',
 'Dorsum Of Foot Pain':'pain on top of the foot','Dorsum Of Hand Swelling':'swelling on the back of the hand','Supraclavicular Fossa Pain':'pain above the collarbone',
 'Subglossal Region Swelling':'swelling under the tongue','Submandibular Region Swelling':'swelling under the jaw','Retro-Auricular Pain':'pain behind the ear',
 'Orbital Ridge Pain':'brow-bone pain','Supraorbital Region Pain':'pain above the eye','Canthus Pain':'pain at the corner of the eye','Outer Canthus Pain':'pain at the outer corner of the eye',
 'Temporal Region Pain':'temple pain','Vertical Headache':'headache at the top of the head','Occipital Headache':'headache at the back of the head','Frontal Region Headache':'forehead headache',
 'Migraine':'migraine','Feverish Sensation On Palm':'hot palms','Palm Feverish Sensation':'hot palms','Sole Feverish Sensation':'hot soles','Burning Feet':'burning feet',
 'Chest Suffocating Sensation':'tight chest','Stuffy Chest':'tight chest','Chest Fullness':'chest fullness','Chest Distension':'chest bloating','Cerebral Circulation Insufficiency':'poor blood flow to the brain',
 'Urine Dribbling':'dribbling urine','Urine Incontinence':'urine leakage','Urine Retention':'inability to pass urine','Reddish Urine':'dark urine','Frequent Urination':'frequent urination',
 'Testis Pain':'testicular pain','Testis Swelling':'testicular swelling','Unchecked Diarrhea':'persistent diarrhoea','Diarrhea':'diarrhoea','Blood Spitting':'spitting blood','Blurred Vision':'blurred vision','Swallow Difficulty':'difficulty swallowing','External Genitalia Pruritus':'genital itching','Vision Failing':'failing eyesight','Glaucoma':'glaucoma','Flaccid Type Apoplexy':'stroke with limpness','Dry Mouth':'dry mouth','Mumps':'mumps','Mouth Bitter Taste':'bitter taste','Chill':'chills','Face Puffiness':'puffy face','Difficult Ingestion':'difficulty eating','Face Flush':'flushed face','Paralysis Due To Stroke':'paralysis after stroke','Backache Refer To Testis':'back pain spreading to the testicles','Face Edema':'facial swelling','Color Blindness':'colour blindness','Pain Due To Hernia':'hernia pain','Cold Sensation':'feeling cold','Abdominal Mass':'abdominal lump','Head Heavy Sensation':'heavy head','Brain Uncomfortable Feeling':'head discomfort','Tongue Dryness':'dry tongue','Acute Infantile Omphalitis':"infant's navel infection",'Foot Fungus Infection':"athlete's foot",'Hand Fungus Infection':'hand fungal infection','Back Heavy Sensation':'heavy back','Shoulder Heavy Sensation':'heavy shoulders','Jaundice Epilepsy':'jaundice with seizures','Dry Throat':'dry throat','Hypertension':'high blood pressure','Swelling Around External Genitalia':'genital swelling','Fullness Sensation':'bloated feeling',
}
GENERIC_MESH = {'Quality of Life','Acute Disease','Chronic Disease','Postoperative Complications','Weight Loss'}
MESH_PLAIN = {'Sleep Initiation and Maintenance Disorders':'insomnia','Pain, Postoperative':'pain after surgery','Postoperative Nausea and Vomiting':'nausea and vomiting after surgery',
 'Osteoarthritis, Knee':'knee osteoarthritis','Rhinitis, Allergic':'hay fever / allergic rhinitis','Rhinitis, Allergic, Seasonal':'seasonal hay fever','Rhinitis, Allergic, Perennial':'year-round allergic rhinitis',
 'Infertility, Female':'female infertility','Angina, Stable':'stable angina','Migraine Disorders':'migraine','Migraine without Aura':'migraine without aura','Fatigue Syndrome, Chronic':'chronic fatigue syndrome',
 'Renal Insufficiency, Chronic':'chronic kidney disease','Substance Withdrawal Syndrome':'withdrawal symptoms','Cognition Disorders':'cognitive problems','Lung Neoplasms':'lung cancer (symptom support)',
 'Dry Eye Syndromes':'dry eyes','Gastroparesis':'slow stomach emptying','Muscle Spasticity':'muscle spasticity','Hot Flashes':'hot flushes','Radiculopathy':'pinched nerve / sciatica','Pruritus':'itching','Colic':'infant colic / colic pain'}
MANUAL = {  # traditional indications for points missing from AcuKG (standard textbooks)
 'ST17': [], 'GV29': ['Headache','Insomnia','Nasal Obstruction','Rhinorrhea','Epistaxis','Dizziness','Infantile Convulsion','Anxiety'],
 'EX-HN1': ['Headache','Vertigo','Insomnia','Poor Memory','Epilepsy','Apoplexy'],
 'EX-HN2': ['Headache','Eye Redness','Eye Pain','Eye Swelling','Nasal Obstruction','Vertigo'],
 'EX-HN4': ['Eye Redness','Eye Pain','Eye Swelling','Eyelid Ptosis','Eyelid Twitching','Supraorbital Region Pain','Blurred Vision'],
 'EX-HN5': ['Headache','Migraine','Temporal Region Pain','Eye Redness','Eye Pain','Face Paralysis','Toothache','Dizziness'],
 'EX-HN6': ['Eye Redness','Eye Pain','Eye Swelling','Fever','Sore Throat','Headache','Hypertension'],
 'EX-HN7': ['Eye Pain','Blurred Vision','Vision Failing','Glaucoma','Night Blindness'],
 'EX-HN8': ['Nasal Obstruction','Rhinorrhea','Frequent Sneezing','Headache','Eye Redness','Eye Pain'],
 'EX-HN9': ['Nasal Obstruction','Heat Stroke','Eye Redness','Eye Swelling'],
 'EX-HN10': ['Asthma','Cough','Tongue Stiffness','Mute'],
 'EX-HN11': ['Thirst','Vomiting','Hiccup','Tongue Stiffness','Aphasia'],
 'EX-HN12': ['Tongue Swelling','Tongue Stiffness','Vomiting','Thirst','Aphasia','Diarrhea'],
 'EX-HN13': ['Tongue Swelling','Tongue Stiffness','Vomiting','Thirst','Aphasia','Diarrhea'],
 'EX-HN14': ['Blurred Vision','Night Blindness','Glaucoma','Tinnitus','Vertigo','Insomnia','Headache'],
 'EX-HN15': ['Neck Stiffness','Neck Pain','Cough','Asthma','Scrofula','Night Sweat'],
 'EX-Anmian': ['Insomnia','Dream-Disturbed Sleep','Headache','Vertigo','Palpitation','Anxiety','Mental Disorder'],
}
MANUAL_SRC = {'id':'textbook','label':'Traditional indication (standard textbooks: Deadman, A Manual of Acupuncture; 经络腧穴学)','url':''}
AK_SRC = {'id':'acukg','label':'Traditional indication — AcuKG knowledge graph (Li et al., JAMIA 2025), compiled from the WHO standard and Acufinder.com','url':'https://doi.org/10.1093/jamia/ocaf179'}
AK_ACT_SRC = {'id':'acukg-actions','label':'TCM actions — AcuKG knowledge graph (Li et al., JAMIA 2025)','url':'https://doi.org/10.1093/jamia/ocaf179'}
PM_SRC = {'id':'pubmed','label':'Clinical studies indexed in PubMed that used this point for the condition (from AcuKG); a study is not proof of benefit','url':'https://pubmed.ncbi.nlm.nih.gov/'}
REVIEWS = {  # curated, verified systematic reviews for the most-used acupressure points
 'PC6': [{'claim':'Reduces nausea and vomiting after surgery (acupressure, wristbands or acupuncture at PC6, alone or with anti-sickness drugs); evidence low to moderate quality.',
          'cite':'Lee A, Zhang JZ, Xie J, Cheng V, Wong MKH, Yau DKW. Stimulation of the wrist acupuncture point PC6 for preventing postoperative nausea and vomiting. Cochrane Database Syst Rev 2025. DOI 10.1002/14651858.CD003281.pub5','url':'https://doi.org/10.1002/14651858.CD003281.pub5','strength':'Cochrane review'}],
 'SP6': [{'claim':'Acupuncture or acupressure at SP6 reduced period pain compared with control in a meta-analysis of randomised trials.',
          'cite':'Chen MN, Chien LW, Liu CF. Acupuncture or acupressure at the Sanyinjiao (SP6) acupoint for the treatment of primary dysmenorrhea: a meta-analysis. Evid Based Complement Alternat Med 2013;2013:493038.','url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC3600281/','strength':'Meta-analysis'},
         {'claim':'Acupressure (mostly at SP6 and LI4) may modestly relieve pain during labour; evidence low to moderate quality.',
          'cite':'Smith CA, Collins CT, Levett KM, Armour M, Dahlen HG, Tan AL, Mesgarpour B. Acupuncture or acupressure for pain management during labour. Cochrane Database Syst Rev 2020. DOI 10.1002/14651858.CD009232.pub2','url':'https://doi.org/10.1002/14651858.CD009232.pub2','strength':'Cochrane review'}],
 'LI4': [{'claim':'Acupressure (mostly at LI4 and SP6) may modestly relieve pain during labour; evidence low to moderate quality.',
          'cite':'Smith CA, Collins CT, Levett KM, Armour M, Dahlen HG, Tan AL, Mesgarpour B. Acupuncture or acupressure for pain management during labour. Cochrane Database Syst Rev 2020. DOI 10.1002/14651858.CD009232.pub2','url':'https://doi.org/10.1002/14651858.CD009232.pub2','strength':'Cochrane review'},
         {'claim':'Acupuncture (LI4 is among the most-used points) is effective for frequent episodic or chronic tension-type headache.',
          'cite':'Linde K, Allais G, Brinkhaus B, et al. Acupuncture for the prevention of tension-type headache. Cochrane Database Syst Rev 2016;(4):CD007587. DOI 10.1002/14651858.CD007587.pub2','url':'https://doi.org/10.1002/14651858.CD007587.pub2','strength':'Cochrane review (acupuncture, not acupressure)'}],
 'HT7': [{'claim':'Acupressure improved sleep quality across randomised trials; HT7 was the most frequently used point.',
          'cite':'Waits A, Tang YR, Cheng HM, Tai CJ, Chien LY. Acupressure effect on sleep quality: a systematic review and meta-analysis. Sleep Med Rev 2018;37:24-34. PMID 28089414','url':'https://pubmed.ncbi.nlm.nih.gov/28089414/','strength':'Meta-analysis'}],
 'GB20': [{'claim':'Acupuncture (GB20 is among the most-used points) is effective for frequent episodic or chronic tension-type headache.',
          'cite':'Linde K, Allais G, Brinkhaus B, et al. Acupuncture for the prevention of tension-type headache. Cochrane Database Syst Rev 2016;(4):CD007587. DOI 10.1002/14651858.CD007587.pub2','url':'https://doi.org/10.1002/14651858.CD007587.pub2','strength':'Cochrane review (acupuncture, not acupressure)'}],
 'EX-HN5': [{'claim':'Acupuncture (Taiyang is among the most-used points) is effective for frequent episodic or chronic tension-type headache.',
          'cite':'Linde K, Allais G, Brinkhaus B, et al. Acupuncture for the prevention of tension-type headache. Cochrane Database Syst Rev 2016;(4):CD007587. DOI 10.1002/14651858.CD007587.pub2','url':'https://doi.org/10.1002/14651858.CD007587.pub2','strength':'Cochrane review (acupuncture, not acupressure)'}],
}
DROP={'Depression Distal To Junction Of The First And Second Metatarsal Bone'}
def norm(t):
    t=t.strip(); t=FIX.get(t,t); return t
def load():
    ind=collections.defaultdict(list)
    for r in csv.DictReader(open(AK+'Indication.csv',encoding='utf-8-sig')):
        t=norm(r['Indication'])
        if t in DROP: continue
        if t not in ind[r['Acupoint_Code']]: ind[r['Acupoint_Code']].append(t)
    act=collections.defaultdict(list)
    for r in csv.DictReader(open(AK+'Action_target.csv',encoding='utf-8-sig')):
        a=f"{r['Relation'].strip()} {r['Action_Target'].strip()}"
        if a not in act[r['Acupoint_Code']]: act[r['Acupoint_Code']].append(a)
    pm=collections.defaultdict(list)
    for r in csv.DictReader(open(AK+'PubMed.csv',encoding='utf-8-sig')):
        if r['Mesh_Term'] in GENERIC_MESH: continue
        pm[r['Acupoint_Code']].append({'condition':r['Mesh_Term'],'plain':MESH_PLAIN.get(r['Mesh_Term'],r['Mesh_Term'].lower()),
                                       'pmids':[p.strip() for p in r['PMIDs'].split(',') if p.strip()]})
    return ind,act,pm
def benefits_for(pid, ind, act, pm):
    if pid in MANUAL: trad=[{'term':t,'plain':GLOSS.get(t,''),'source':'textbook'} for t in MANUAL[pid]]
    else: trad=[{'term':t,'plain':GLOSS.get(t,''),'source':'acukg'} for t in ind.get(pid,[])]
    return {'traditional':trad,'actions':act.get(pid,[]),'studies':sorted(pm.get(pid,[]),key=lambda s:-len(s['pmids'])),'reviews':REVIEWS.get(pid,[])}
SOURCES=[AK_SRC,MANUAL_SRC,AK_ACT_SRC,PM_SRC]
