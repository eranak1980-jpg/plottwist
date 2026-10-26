"""Short, grounded opening rounds. No external calls; no invented player facts."""
PACKS = {
'en': {
'friends': [
('A friend cancels plans with {s} an hour before. What does {s} do?', ['Makes other plans','Asks what happened','Suggests another day','Enjoys the free evening']),
('{s} gets the restaurant bill after ordering less than everyone. What happens?', ['Splits it equally','Pays for their own food','Suggests separate bills','Lets someone else decide']),
('The group cannot pick a restaurant. What does {s} do?', ['Chooses a place','Starts a vote','Suggests eating at home','Follows the final choice']),
('A friend returns a borrowed hoodie late. What matters most to {s}?', ['Getting it back','Hearing an apology','Knowing it is clean','It was never a problem']),
('{s} is the first to arrive at a party. What happens?', ['Helps the host','Texts the group','Starts a conversation','Finds the snacks']),
('A friend gives {s} a gift they would never choose. How does {s} respond?', ['Thanks them warmly','Asks about an exchange','Saves it for later','Tries it anyway']),
],
'couple': [
('{s} and their partner have a free evening. What would {s} suggest?', ['Cooking together','Going out for dinner','Watching a film','Taking a walk']),
('After a small disagreement, what does {s} usually do first?', ['Starts a conversation','Takes some quiet time','Makes a gentle joke','Offers a small gesture']),
('Their partner plans a surprise outing. What would {s} prefer?', ['Knowing the destination','One small clue','A complete surprise','Choosing the time together']),
('{s} wants to show affection on an ordinary day. What feels most natural?', ['A thoughtful message','Making a favourite meal','A hug','Planning time together']),
('The two cannot agree on a film. What does {s} suggest?', ['Taking turns choosing','Trying something new','Watching one episode','Doing something else together']),
('A weekend away starts tomorrow. What has {s} already planned?', ['The whole itinerary','A restaurant booking','Only the journey','A few possible activities']),
],
'family': [
('At a family meal, what does {s} do first?', ['Helps in the kitchen','Catches up with everyone','Checks the menu','Sets the table']),
('The family finds old photos. What does {s} do?', ['Tells the stories','Sends some to the group','Looks for childhood photos','Asks who everyone is']),
('A family outing needs organizing. What would {s} take care of?', ['Choosing the place','Bringing food','Arranging transport','Keeping everyone updated']),
('Someone suggests a family photo. What does {s} do?', ['Organizes everyone','Takes the photo','Suggests a funny pose','Joins without a fuss']),
('There is one slice of cake left. What does {s} do?', ['Offers it to someone','Cuts it into pieces','Asks who wants it','Saves it for later']),
('A relative asks {s} for help with a phone. What happens?', ['Explains each step','Fixes it directly','Writes down instructions','Finds a helpful video']),
]},
'he': {
'friends': [
('חבר מבטל תוכנית עם {s} שעה לפני. מה התגובה?', ['מוצאים תוכנית אחרת','שואלים מה קרה','קובעים ליום אחר','נהנים מהערב שהתפנה']),
('במסעדה {s} הזמין פחות מכולם. איך מחלקים את החשבון?', ['מתחלקים שווה','משלמים לפי ההזמנה','מבקשים חשבונות נפרדים','נותנים לאחרים להחליט']),
('החבורה לא מצליחה לבחור מסעדה. מה {s} עושה?', ['בוחר מקום','פותח הצבעה','מציע לאכול בבית','זורם עם ההחלטה']),
('חבר מחזיר ל־{s} בגד באיחור. מה הכי חשוב?', ['שהבגד חזר','לשמוע התנצלות','שהבגד נקי','האיחור לא הפריע']),
('{s} מגיע ראשון למסיבה. מה קורה?', ['עוזרים למארח','כותבים בקבוצה','פותחים בשיחה','מוצאים את החטיפים']),
('{s} מקבל מתנה שלא היה בוחר בעצמו. איך מגיבים?', ['מודים בחום','שואלים על החלפה','שומרים להזדמנות אחרת','נותנים לה הזדמנות']),
],
'couple': [
('ל־{s} ולבן או בת הזוג יש ערב פנוי. מה ההצעה?', ['לבשל יחד','לצאת למסעדה','לראות סרט','לצאת להליכה']),
('אחרי ויכוח קטן בזוגיות, מה {s} עושה קודם?', ['פותחים בשיחה','לוקחים קצת זמן בשקט','מנסים בדיחה עדינה','עושים מחווה קטנה']),
('מתכננים ל־{s} בילוי בהפתעה. מה עדיף מבחינתו?', ['לדעת לאן הולכים','לקבל רמז קטן','הפתעה מוחלטת','לבחור יחד את השעה']),
('איך הכי טבעי ל־{s} להראות חיבה ביום רגיל?', ['הודעה מתחשבת','הכנת אוכל אהוב','חיבוק','תכנון זמן משותף']),
('לא מצליחים להסכים על סרט. מה {s} מציע?', ['לבחור לפי תור','לנסות משהו חדש','לראות פרק בסדרה','לעשות משהו אחר יחד']),
('מחר יוצאים לחופשה זוגית. מה {s} כבר תכנן?', ['את כל המסלול','הזמנה למסעדה','רק את הנסיעה','כמה פעילויות אפשריות']),
],
'family': [
('בארוחה משפחתית, מה {s} עושה קודם?', ['עוזרים במטבח','מתעדכנים עם כולם','בודקים מה אוכלים','עורכים את השולחן']),
('המשפחה מוצאת תמונות ישנות. מה {s} עושה?', ['מספרים את הסיפורים','שולחים כמה לקבוצה','מחפשים תמונות ילדות','שואלים מי מופיע בתמונה']),
('צריך לארגן טיול משפחתי. על מה {s} ייקח אחריות?', ['בחירת המקום','הבאת האוכל','סידור ההסעות','עדכונים לכל המשפחה']),
('מישהו מציע צילום משפחתי. מה {s} עושה?', ['מארגנים את כולם','מצלמים','מציעים פוזה מצחיקה','מצטרפים בלי עניין']),
('נשארה פרוסת עוגה אחת. מה {s} עושה?', ['מציעים אותה לאחר','חותכים לכמה חתיכות','שואלים מי רוצה','שומרים לאחר כך']),
('קרוב משפחה מבקש מ־{s} עזרה בטלפון. מה קורה?', ['מסבירים שלב אחרי שלב','מתקנים בעצמנו','כותבים הוראות','מוצאים סרטון הדרכה']),
]}}

def opening_pack(language,context,topics):
 bank=PACKS.get(language)
 if not bank:return []
 context=str(context or '').casefold()
 family=any(word in context for word in ('family','משפחה','familia','famille','家族')) or 'משפחה' in topics
 couple=any(word in context for word in ('couple','זוג','pareja','casal','カップル'))
 kind='family' if family else 'couple' if couple else 'friends'
 # Narrow themes selected in advanced settings keep their existing targeted pack.
 allowed={'מה היית עושה אם…','סודות והרגלים','חברות ואמון','משפחה','זוגיות','אוכל'}
 if topics and any(t not in allowed for t in topics):return []
 return [('know',text,options) for text,options in bank[kind]]
