"""Explicit Hebrew inflections. Never infer gender from a name or a photograph."""
import re

# Subject-only question replacements: other people in the situation keep their gender.
QUESTION_PAIRS = {
 'מישהו פגע ב־{s} ואז כתב כאילו לא קרה כלום. איך מגיבים?': ('חבר אמר ל־{s} משהו מעליב. למחרת הוא שולח הודעה רגילה בלי להתנצל. איך {s} מגיב/ה?', ['מדבר/ת איתו על מה שקרה','עונה בקצרה ובקור','עונה כרגיל','לא עונה']),
 'החבורה בוחרת מסעדה ש־{s} לא אוהב. מה הוא עושה?': ('החבורה בוחרת מסעדה ש־{s} לא אוהב/ת. מה {s} עושה?', ['מציע/ה מקום אחר','מצטרף/ת בכל זאת','מצטרף/ת אחרי הארוחה','מבקש/ת מחבר לתמוך בהצעה אחרת']),
}
# These verbs refer to the spotlight player, not the friend in the setup.
WORDS = dict(zip(
 'אוהב מציע מצטרף מבקש אומר קורא מגיב שואל מוחק מתקשר מחכה שולח כותב מחפש מחליף מסיים בודק מסביר שותק חושב מחזיר צוחק משלם מעיר מנסה מתבאס משכנע זוכר משחזר עשה עונה מעדיף מבין מצחיק מסרב קובע מלווה מפרגן מפסיק מתרחק רומז מרגיש יוזם תומך מתערב מארח חוזר מזמין חולק מספר מקבל יודע מאחר הזמין קיבל ראה קנה גילה הפסיד הוזמן נפגע'.split(),
 'אוהבת מציעה מצטרפת מבקשת אומרת קוראת מגיבה שואלת מוחקת מתקשרת מחכה שולחת כותבת מחפשת מחליפה מסיימת בודקת מסבירה שותקת חושבת מחזירה צוחקת משלמת מעירה מנסה מתבאסת משכנעת זוכרת משחזרת עשתה עונה מעדיפה מבינה מצחיקה מסרבת קובעת מלווה מפרגנת מפסיקה מתרחקת רומזת מרגישה יוזמת תומכת מתערבת מארחת חוזרת מזמינה חולקת מספרת מקבלת יודעת מאחרת הזמינה קיבלה ראתה קנתה גילתה הפסידה הוזמנה נפגעה'.split()))
WORDS.update({'הוא':'היא','אותו':'אותה','עליו':'עליה','אליו':'אליה','עצמו':'עצמה','לו':'לה','בו':'בה','ממנו':'ממנה','מולו':'מולה','בלעדיו':'בלעדיה','שלו':'שלה','דעתו':'דעתה','אתה':'את','שנפגע':'שנפגעה','שמעכב':'שמעכבת'})
# Whose action is the answer? Keep male friends, gifts and partners intact.
OTHER_PERSON_OPTIONS = ('מה יותר מפריע','מספר לחבר חדשות טובות','איזו התנצלות','מתחיל לצאת עם האקס','הסתיר ממנו משהו','איזה הרגל של חבר')
SUBJECT_QUESTION_PHRASES = {
 '{s} מגלה שחברים נפגשו בלעדיו':'{s} מגלה שחברים נפגשו בלעדיו/בלעדיה',
 '{s} כתב הודעה ולא קיבל תשובה, אבל ראה':'{s} כתב/ה הודעה ולא קיבל/ה תשובה, אבל ראה/ראתה',
 '{s} הפסיד במשחק וכולם חוגגים מולו':'{s} הפסיד/ה במשחק וכולם חוגגים מולו/מולה',
 'ל־{s} שהוא מאחר תמיד. איך הוא מגיב':'ל־{s} על איחור חוזר. איך {s} מגיב/ה',
 '{s} הזמין פחות':'{s} הזמין/ה פחות',
 'מה הכי קשה לו':'מה הכי קשה ל־{s}',
 'לא להראות שהוא יודע':'לא להראות שיש לך מידע',
 'כולם יצאו טוב חוץ ממנו':'כולם יצאו טוב חוץ מ־{s}',
 'ביקורת שהוא לא מסכים איתה':'ביקורת שלא מקובלת על {s}',
 '{s} קנה משהו יקר ואז גילה':'{s} קנה/קנתה משהו יקר ואז גילה/גילתה',
 '{s} קיבל הודעה':'{s} קיבל/ה הודעה',
 'בדיחה שפגעה בו':'בדיחה שפגעה ב־{s}',
 '{s} צריך לבחור':'{s} צריך/ה לבחור',
 'דעתו של {s}':'הדעה של {s}',
 '{s} מספר לחבר':'{s} מספר/ת לחבר',
 'תאכזב אותו':'תאכזב את {s}',
 'מה {s} מבקש':'מה {s} מבקש/ת',
 '{s} מארח הערב':'{s} מארח/ת הערב',
 '{s} חוזר למסעדה שהוא אוהב':'{s} חוזר/ת למסעדה אהובה',
 '{s} מספר לחבר על יום קשה ומקבל עצות שלא ביקש':'{s} מספר/ת לחבר על יום קשה ומקבל/ת עצות בלי לבקש',
 '{s} חולק חדר':'{s} חולק/ת חדר',
 'ו־{s} חושב שהוא טועה':'ו־{s} לא מסכים/ה איתו',
 '{s} מגלה שחבר הסתיר ממנו משהו':'{s} מגלה שחבר הסתיר מידע מ־{s}',
 'מה הכי מפריע לו':'מה הכי מפריע ל־{s}',
 '{s} מרגיש שרק הוא יוזם':'{s} מרגיש/ה שרק הוא/היא יוזם/ת',
 'מתי הוא אומר אותה':'מתי {s} אומר/ת אותה',
 'מה הוא עושה':'מה {s} עושה', 'מה הוא מבקש':'מה {s} מבקש/ת', 'מה הוא מזמין':'מה {s} מזמין/ה',
}

# Reviewed exceptions preserve the role of the other friend, rather than applying
# a blanket replacement to every masculine word in a sentence.
OPTION_FEMALE = {
 'שואל למה לא הוזמן':'שואלת למה לא הוזמנה', 'מסביר למה איחר הפעם':'מסבירה למה איחרה הפעם',
 'צוחק ומעביר נושא':'צוחקת ומעבירה נושא', 'לא להראות שהוא יודע':'לא להראות שהיא יודעת',
 'מחזיר ביקורת משלו':'מחזירה ביקורת משלה', 'אומר שזה מפריע לו':'אומרת שזה מפריע לה',
 'מתבאס וממשיך הלאה':'מתבאסת וממשיכה הלאה', 'אומר שהרעיון שלו':'אומרת שהרעיון שלה',
 'אומר שנפגע מול כולם':'אומרת שנפגעה מול כולם', 'צוחק למרות שנפגע':'צוחקת למרות שנפגעה',
 'אומר שמעדיף לדבר בפרטי':'אומרת שמעדיפה לדבר בפרטי', 'אתה מצחיק אותי':'את מצחיקה אותי',
 'אתה מבין אותי':'את מבינה אותי', 'בודק שלא שכח כלום':'בודקת שלא שכחה כלום',
 'מחכה שמישהו יציע לו':'מחכה שמישהו יציע לה', 'אומר שזה לא מתאים לו':'אומרת שזה לא מתאים לה',
 'אומר שהוא לא מסכים':'אומרת שהיא לא מסכימה', 'תומך בו ומדבר איתו אחר כך':'תומכת בו ומדברת איתו אחר כך',
 'שלא סמכו עליו':'שלא סמכו עליה', 'שהאחרים ידעו לפניו':'שהאחרים ידעו לפניה',
 'שלא סיפרו לו ישירות':'שלא סיפרו לה ישירות', 'רק אם שואלים אותו':'רק אם שואלים אותה',
 'שישמע על זה מהחבר':'שתשמע על זה מהחבר', 'שלא ידברו איתו על הקשר':'שלא ידברו איתה על הקשר',
}
NEUTRAL_OPTIONS = {
 'מתקנים מול כולם':'לתקן מול כולם', 'מתקנים אותו אחר כך':'לדבר איתו אחר כך',
 'זורמים עם הסיפור':'לזרום עם הסיפור', 'מוסיפים בצחוק גרסה משלהם':'להוסיף בצחוק גרסה אחרת',
 'מלווים בלי לשאול':'להלוות בלי לשאול', 'קובעים מועד להחזרה':'לקבוע מועד להחזרה',
 'מלווים סכום קטן יותר':'להלוות סכום קטן יותר', 'מסרבים להלוות':'לסרב להלוות',
 'קובעים רק מקום ראשון':'לקבוע רק את המקום הראשון','בוחרים ברגע האחרון':'לבחור ברגע האחרון',
 'נותנים לחבר להחליט':'לתת לחבר להחליט','עוצרים ומסבירים':'לעצור ולהסביר',
 'מתחילים את הסיבוב מחדש':'להתחיל את הסיבוב מחדש','ממשיכים ומסבירים בסוף':'להמשיך ולהסביר בסוף',
 'נותנים לו הזדמנות נוספת':'לתת לו הזדמנות נוספת','אומרים ישר מה לא עובד':'לומר ישר מה לא עובד',
 'מתחילים במה שכן טוב':'להתחיל במה שכן טוב','שואלים כמה כנות הוא רוצה':'לשאול כמה כנות הוא רוצה',
 'מציעים שינוי אחד קטן':'להציע שינוי אחד קטן',
}
WORDS.update(dict(zip('מדבר מתווכח מעביר נותן מתחיל ממשיך מגיע מכיר נשאר מציג הולך רעב לוקח מזכיר מסכים מסדר מתעלם'.split(),
                     'מדברת מתווכחת מעבירה נותנת מתחילה ממשיכה מגיעה מכירה נשארת מציגה הולכת רעבה לוקחת מזכירה מסכימה מסדרת מתעלמת'.split())))
SUBJECT_QUESTION_PHRASES.update({
 '{s} מקבל ביקורת':'{s} מקבל/ת ביקורת',
 '{s} מגיע למסיבה ומכיר':'{s} מגיע/ה למסיבה ומכיר/ה',
 'ו־{s} עדיין רעב':'ו־{s} עדיין רעב/ה',
 'סיפור לא מדויק על ערב שהיה בו':'סיפור לא מדויק על ערב שבו שניהם היו',
})

def forms(text,gender):
 def slash(m):
  a,b=m.group(1),m.group(2)
  if not (len(b)==1 or b in ('תה','תי','ית') or (a.startswith('י') and b.startswith('ת') and a[1:]==b[1:]) or WORDS.get(a)==b or (a,b) in (('הוא','היא'),('לו','לה'),('בו','בה'),('מולו','מולה'),('בלעדיו','בלעדיה'),('קנה','קנתה'),('ראה','ראתה'),('גילה','גילתה'),('צריך','צריכה'),('ראשון','ראשונה'))):return m.group()
  if gender=='unspecified':return m.group()
  if gender=='male':return a
  if a in WORDS:return WORDS[a]
  if (a,b)==('היה','תה'):return 'הייתה'
  if len(b)==1 and a.endswith(b):return a
  if len(b)==1:return a[:-1]+a[-1].translate(str.maketrans('ךםןףץ','כמנפצ'))+b
  if b in ('תה','תי','ית'):return a[:-1]+b if a.endswith(('ה','ת')) else a+b
  return b
 return re.sub(r'([א-ת]+)/(היא|[א-ת]+)',slash,text)

def gender_card(text,options,typ,subject,players):
 gender=subject['gender'] if subject['gender'] in ('male','female') else 'unspecified'
 # Protect complete names before any grammar replacement (e.g. a player named עונה).
 protected={p['name']:f'__PLAYER_{i}__' for i,p in enumerate(players)}
 name=subject['name'];template=text.replace(name,'{s}')
 known=template in QUESTION_PAIRS
 if known:template,options=QUESTION_PAIRS[template]
 subject_options=not any(x in template for x in OTHER_PERSON_OPTIONS)
 for a,b in sorted(SUBJECT_QUESTION_PHRASES.items(),key=lambda x:len(x[0]),reverse=True):template=template.replace(a,b)
 template=template.replace('{s}',name)
 def render(value,inflect=False):
  if value in NEUTRAL_OPTIONS:value=NEUTRAL_OPTIONS[value]
  if gender=='female' and value in OPTION_FEMALE:return OPTION_FEMALE[value]
  for n,marker in sorted(protected.items(),key=lambda x:len(x[0]),reverse=True):
   value=re.sub(r'(?<!\w)'+re.escape(n)+r'(?!\w)',marker,value)
  value=forms(value,gender)
  if inflect:
   # Only the first action and coordinated actions describe the subject.
   # Do not feminize the friend in "לשאול אם הוא אוהב אותה".
   words=value.split(' ')
   position=1 if words and words[0]=='לא' else 0
   positions={position}
   for i,w in enumerate(words):
    if i and (w.startswith('ו') and w[1:] in WORDS or words[i-1]=='אבל'):positions.add(i)
   for i in positions:
    if i>=len(words):continue
    v=words[i];female=WORDS.get(v)
    if female is None and v.startswith('ו') and v[1:] in WORDS:female='ו'+WORDS[v[1:]]
    if female and female!=v and '/' not in v:
     words[i]=female if gender=='female' else v if gender=='male' else v+'/'+female
   value=' '.join(words)
   owned={'עצמו':('עצמו','עצמה'),'התקציב שלו':('התקציב שלו','התקציב שלה'),'שהוא הולך לישון':('שהוא הולך לישון','שהיא הולכת לישון'),'מה אולי עשה':('מה אולי עשה','מה אולי עשתה'),'אתה מצחיק אותי':('אתה מצחיק אותי','את מצחיקה אותי'),'אתה מבין אותי':('אתה מבין אותי','את מבינה אותי')}
   for phrase,(male,female) in owned.items():
    value=value.replace(phrase,female if gender=='female' else male if gender=='male' else male+'/'+female)
  for n,marker in protected.items():value=value.replace(marker,n)
  return value
 # Only subject-specific phrases have been marked in questions. Options describe
 # the subject except the explicit cards about another person's behavior.
 return render(template),list(options) if typ=='room' else [render(o,subject_options and not known) for o in options]
