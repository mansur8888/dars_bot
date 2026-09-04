import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiohttp import web

TOKEN = "8685388983:AAFwjfV-RvOrq4vT1hI_SxIqIPd0-lZ6cZg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# FSM Holatlari
class DarsTaqsimot(StatesGroup):
    category = State()
    subject = State()
    total_hours = State()
    teacher_count = State()
    teacher_name = State()
    teachers_data = State()

# 2026-2027 o'quv yili tayanch o'quv rejasiga mos to'liq fanlar ro'yxati
SUBJECTS_YUQORI = [
    "Ona tili", 
    "O'zbek tili / Davlat tili", 
    "Adabiyot", 
    "Matematika (Algebra / Geometriya)", 
    "Chet tili (Ingliz/Nemis/Fransuz)", 
    "Ikkinchi chet tili",
    "Tarix (O'zbekiston tarixi / Jahon tarixi)", 
    "Huquqshunoslik (Davlat va huquq asoslari)", 
    "Geografiya", 
    "Fizika", 
    "Kimyo", 
    "Biologiya", 
    "Tabiiy fan (Science)", 
    "Informatika va axborot texnologiyalari", 
    "Tarbiya", 
    "Jismoniy tarbiya", 
    "Texnologiya", 
    "Tasviriy san'at va chizmachilik", 
    "Musiqa madaniyati", 
    "CHYOT (Chaqiriqqa qadar boshlang'ich tayyorgarlik)"
]

SUBJECTS_BOSHLANGICH = [
    "O'qish savodxonligi / Ona tili", 
    "Matematika", 
    "Tabiiy fan (Science)", 
    "Tarbiya", 
    "Tasviriy san'at", 
    "Musiqa madaniyati", 
    "Texnologiya", 
    "Jismoniy tarbiya", 
    "Chet tili (Boshlang'ich)"
]

# Asosiy klaviatura
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏫 Boshlang'ich sinflar (18 soat/stavka)"), KeyboardButton(text="🎓 Yuqori sinflar (20 soat/stavka)")],
        [KeyboardButton(text="📜 Nizom bo'yicha ketma-ketlik")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>3271-sonli Qaror va 2026-2027 o'quv yili Nizomi asosida Dars soatlarini taqsimlash botiga xush kelibsiz!</b>\n\n"
        "Iltimos, ta'lim bosqichini tanlang:",
        parse_mode="HTML",
        reply_markup=main_kb
    )

@dp.message(F.text == "📜 Nizom bo'yicha ketma-ketlik")
async def info_nizom(message: types.Message):
    text = (
        "<b>Dars soatlarini taqsimlashning 10 bosqichli Rasmiy Ketma-ketligi:</b>\n\n"
        "1️⃣ Oliy malaka toifasiga ega o'qituvchilar;\n"
        "2️⃣ Milliy yoki Xalqaro sertifikatga ega o'qituvchilar;\n"
        "3️⃣ Birinchi malaka toifasiga ega o'qituvchilar;\n"
        "4️⃣ Ikkinchi malaka toifasiga ega o'qituvchilar;\n"
        "5️⃣ Oliy ma'lumotli toifasiz (mutaxassis) o'qituvchilar;\n"
        "6️⃣ Qayta tayyorlash bo'yicha diplomga ega o'qituvchilar;\n"
        "7️⃣ O'rindoshlik asosida ishlayotgan oliy ma'lumotli o'qituvchilar;\n"
        "8️⃣ OTM 3-kurs va undan yuqori kurs talabalari;\n"
        "9️⃣ O'rta maxsus, professional ma'lumotli o'qituvchilar (faqat boshlang'ich);\n"
        "🔟 Rahbar xodimlar (direktor va o'rinbosarlar).\n\n"
        "📌 <b>Stavka me'yorlari:</b>\n"
        "• Boshlang'ich sinflarda 1 stavka = <b>18 soat</b>\n"
        "• Yuqori sinflarda 1 stavka = <b>20 soat</b>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.in_(["🏫 Boshlang'ich sinflar (18 soat/stavka)", "🎓 Yuqori sinflar (20 soat/stavka)"]))
async def select_category(message: types.Message, state: FSMContext):
    is_boshlangich = "Boshlang'ich" in message.text
    await state.update_data(
        category="boshlangich" if is_boshlangich else "yuqori",
        rate=18 if is_boshlangich else 20
    )
    
    subjects = SUBJECTS_BOSHLANGICH if is_boshlangich else SUBJECTS_YUQORI
    
    # Inline tugmalarni har bir qatorga bittadan yoki qulay tartibda joylaymiz
    kb_list = [[InlineKeyboardButton(text=sub, callback_data=f"sub_{i}")] for i, sub in enumerate(subjects)]
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    
    await state.set_state(DarsTaqsimot.subject)
    await message.answer("<b>Fanni tanlang:</b>", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(DarsTaqsimot.subject, F.data.startswith("sub_"))
async def select_subject(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    subjects = SUBJECTS_BOSHLANGICH if data['category'] == "boshlangich" else SUBJECTS_YUQORI
    selected_sub = subjects[idx]
    
    await state.update_data(subject_name=selected_sub)
    await state.set_state(DarsTaqsimot.total_hours)
    
    await callback.message.edit_text(
        f"<b>Fan:</b> {selected_sub}\n\n"
        f"Ushbu fan bo'yicha maktabdagi <b>jami dars soatini</b> kiriting (Masalan: 52):",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(DarsTaqsimot.total_hours)
async def process_total_hours(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting (Masalan: 52):")
        return
    
    total = int(message.text)
    await state.update_data(total_hours=total)
    await state.set_state(DarsTaqsimot.teacher_count)
    
    await message.answer("Ushbu fan bo'yicha <b>nechta o'qituvchi</b> bor? (Raqam kiriting, masalan: 3):", parse_mode="HTML")

@dp.message(DarsTaqsimot.teacher_count)
async def process_teacher_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Iltimos, to'g'ri o'qituvchilar sonini kiriting:")
        return
    
    count = int(message.text)
    await state.update_data(teacher_count=count, current_teacher=1, teachers=[])
    
    await state.set_state(DarsTaqsimot.teacher_name)
    await message.answer("<b>1-o'qituvchining F.I.Sh. (Familiyasi, Ismi, Sharifi)ni kiriting:</b>\n<i>(Masalan: Salomov Mansur Saatovich)</i>", parse_mode="HTML")

@dp.message(DarsTaqsimot.teacher_name)
async def process_teacher_name(message: types.Message, state: FSMContext):
    t_name = message.text.strip()
    await state.update_data(current_teacher_name=t_name)
    
    data = await state.get_data()
    await ask_teacher_category(message, state, data['current_teacher'], t_name)

async def ask_teacher_category(event, state: FSMContext, teacher_num: int, teacher_name: str):
    data = await state.get_data()
    is_boshlangich = data['category'] == "boshlangich"

    buttons = [
        [InlineKeyboardButton(text="1. Oliy toifali o'qituvchi", callback_data="t_1")],
        [InlineKeyboardButton(text="2. Sertifikatli o'qituvchi (Milliy/Xalqaro)", callback_data="t_2")],
        [InlineKeyboardButton(text="3. Birinchi toifali o'qituvchi", callback_data="t_3")],
        [InlineKeyboardButton(text="4. Ikkinchi toifali o'qituvchi", callback_data="t_4")],
        [InlineKeyboardButton(text="5. Oliy ma'lumotli toifasiz", callback_data="t_5")],
        [InlineKeyboardButton(text="6. Qayta tayyorlash diplomli", callback_data="t_6")],
        [InlineKeyboardButton(text="7. O'rindosh o'qituvchi", callback_data="t_7")],
        [InlineKeyboardButton(text="8. OTM 3-4 kurs talabasi", callback_data="t_8")]
    ]
    
    if is_boshlangich:
        buttons.append([InlineKeyboardButton(text="9. O'rta maxsus (Professional)", callback_data="t_9")])
        
    buttons.append([InlineKeyboardButton(text="10. Rahbar xodim", callback_data="t_10")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    msg_text = f"<b>{teacher_name}</b> ning maqomi/toifasini tanlang:"
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(msg_text, parse_mode="HTML", reply_markup=kb)
    else:
        await event.answer(msg_text, parse_mode="HTML", reply_markup=kb)
    
    await state.set_state(DarsTaqsimot.teachers_data)

@dp.callback_query(DarsTaqsimot.teachers_data, F.data.startswith("t_"))
async def process_teacher_data(callback: types.CallbackQuery, state: FSMContext):
    step_num = int(callback.data.replace("t_", ""))
    data = await state.get_data()
    
    teachers = data['teachers']
    
    names = {
        1: "Oliy toifali",
        2: "Sertifikatli (Milliy/Xalqaro)",
        3: "1-toifali",
        4: "2-toifali",
        5: "Oliy ma'lumotli toifasiz",
        6: "Qayta tayyorlash diplomli",
        7: "O'rindosh o'qituvchi",
        8: "OTM talabasi",
        9: "O'rta maxsus (Professional)",
        10: "Rahbar xodim"
    }
    
    teachers.append({
        "id": data['current_teacher'],
        "fish": data['current_teacher_name'],
        "step": step_num,
        "status_name": names[step_num]
    })
    
    current = data['current_teacher']
    total_teachers = data['teacher_count']
    
    if current < total_teachers:
        next_num = current + 1
        await state.update_data(teachers=teachers, current_teacher=next_num)
        await state.set_state(DarsTaqsimot.teacher_name)
        await callback.message.edit_text(
            f"<b>{next_num}-o'qituvchining F.I.Sh. (Familiyasi, Ismi, Sharifi)ni kiriting:</b>", 
            parse_mode="HTML"
        )
    else:
        await calculate_and_show(callback.message, state, data, teachers)
    await callback.answer()

async def calculate_and_show(message: types.Message, state: FSMContext, data: dict, teachers: list):
    rate = data['rate'] # 18 yoki 20 soat (1 stavka)
    max_single_rate = rate
    total_hours = data['total_hours']
    
    # Rasmiy 10 ta ketma-ketlik bo'yicha o'qituvchilarni saralash
    sorted_teachers = sorted(teachers, key=lambda x: x['step'])
    
    remaining_hours = total_hours
    results = []
    
    # 1-bosqich: Har bir o'qituvchiga navbat bilan 1 stavkadan taqsimlash
    for t in sorted_teachers:
        if remaining_hours <= 0:
            assigned = 0
        else:
            assigned = min(remaining_hours, max_single_rate)
            remaining_hours -= assigned
        
        results.append((t, assigned))
    
    # 2-bosqich: Ortiqcha soatlarni ustuvorlarga (1, 2, 3-toifaga) 1.5 stavkagacha taqsimlash
    if remaining_hours > 0:
        updated_results = []
        for t, h in results:
            if remaining_hours > 0:
                if t['step'] in [1, 2, 3]:
                    can_take = (rate * 1.5) - h
                    if can_take > 0:
                        add_h = min(remaining_hours, can_take)
                        h += add_h
                        remaining_hours -= add_h
            updated_results.append((t, h))
        results = updated_results

    res_text = (
        f"📊 <b>DARS TAQSIMOTI NATIJASI (RASMIY NIZOM BO'YICHA)</b>\n\n"
        f"🔹 <b>Fan:</b> {data['subject_name']}\n"
        f"🔹 <b>Jami dars soati:</b> {total_hours} soat\n"
        f"🔹 <b>1 stavka me'yori:</b> {rate} soat\n"
        f"🔹 <b>O'qituvchilar soni:</b> {len(teachers)} nafar\n\n"
        f"<b>Ustuvor ketma-ketlik bo'yicha taqsimot:</b>\n"
    )
    
    for idx, (t, h) in enumerate(results, 1):
        stavka = round(h / rate, 2)
        res_text += (
            f"\n<b>{idx}. {t['fish']}</b>\n"
            f" └ Maqomi: <i>{t['status_name']} ({t['step']}-o'rin)</i>\n"
            f" └ Dars soati: <b>{h} soat</b> ({stavka} stavka)\n"
        )
    
    if remaining_hours > 0:
        res_text += f"\n⚠️ <b>Eslatma:</b> Taqsimlanmay qolgan dars soati: <b>{remaining_hours} soat</b>."
    
    await message.answer(res_text, parse_mode="HTML", reply_markup=main_kb)
    await state.clear()

# Web server (Render uchun)
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
                          # Asosiy klaviatura
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏫 Boshlang'ich sinflar (18 soat/stavka)"), KeyboardButton(text="🎓 Yuqori sinflar (20 soat/stavka)")],
        [KeyboardButton(text="📜 Nizom bo'yicha ketma-ketlik")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>3271-sonli Qaror va Nizom asosida Dars soatlarini taqsimlash botiga xush kelibsiz!</b>\n\n"
        "Iltimos, ta'lim bosqichini tanlang:",
        parse_mode="HTML",
        reply_markup=main_kb
    )

@dp.message(F.text == "📜 Nizom bo'yicha ketma-ketlik")
async def info_nizom(message: types.Message):
    text = (
        "<b>Dars soatlarini taqsimlashning 10 bosqichli Rasmiy Ketma-ketligi:</b>\n\n"
        "1️⃣ Oliy malaka toifasiga ega o'qituvchilar;\n"
        "2️⃣ Milliy yoki Xalqaro sertifikatga ega o'qituvchilar;\n"
        "3️⃣ Birinchi malaka toifasiga ega o'qituvchilar;\n"
        "4️⃣ Ikkinchi malaka toifasiga ega o'qituvchilar;\n"
        "5️⃣ Oliy ma'lumotli toifasiz (mutaxassis) o'qituvchilar;\n"
        "6️⃣ Qayta tayyorlash bo'yicha diplomga ega o'qituvchilar;\n"
        "7️⃣ O'rindoshlik asosida ishlayotgan oliy ma'lumotli o'qituvchilar;\n"
        "8️⃣ OTM 3-kurs va undan yuqori kurs talabalari;\n"
        "9️⃣ O'rta maxsus, professional ma'lumotli o'qituvchilar (faqat boshlang'ich);\n"
        "🔟 Rahbar xodimlar (direktor va o'rinbosarlar).\n\n"
        "📌 <b>Stavka me'yorlari:</b>\n"
        "• Boshlang'ich sinflarda 1 stavka = <b>18 soat</b>\n"
        "• Yuqori sinflarda 1 stavka = <b>20 soat</b>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text.in_(["🏫 Boshlang'ich sinflar (18 soat/stavka)", "🎓 Yuqori sinflar (20 soat/stavka)"]))
async def select_category(message: types.Message, state: FSMContext):
    is_boshlangich = "Boshlang'ich" in message.text
    await state.update_data(
        category="boshlangich" if is_boshlangich else "yuqori",
        rate=18 if is_boshlangich else 20
    )
    
    subjects = SUBJECTS_BOSHLANGICH if is_boshlangich else SUBJECTS_YUQORI
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=sub, callback_data=f"sub_{i}")] for i, sub in enumerate(subjects)]
    )
    
    await state.set_state(DarsTaqsimot.subject)
    await message.answer("<b>Fanni tanlang:</b>", parse_mode="HTML", reply_markup=kb)

@dp.callback_query(DarsTaqsimot.subject, F.data.startswith("sub_"))
async def select_subject(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_")[1])
    data = await state.get_data()
    subjects = SUBJECTS_BOSHLANGICH if data['category'] == "boshlangich" else SUBJECTS_YUQORI
    selected_sub = subjects[idx]
    
    await state.update_data(subject_name=selected_sub)
    await state.set_state(DarsTaqsimot.total_hours)
    
    await callback.message.edit_text(
        f"<b>Fan:</b> {selected_sub}\n\n"
        f"Ushbu fan bo'yicha maktabdagi <b>jami dars soatini</b> kiriting (Masalan: 52):",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(DarsTaqsimot.total_hours)
async def process_total_hours(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting (Masalan: 52):")
        return
    
    total = int(message.text)
    await state.update_data(total_hours=total)
    await state.set_state(DarsTaqsimot.teacher_count)
    
    await message.answer("Ushbu fan bo'yicha <b>nechta o'qituvchi</b> bor? (Raqam kiriting, masalan: 3):", parse_mode="HTML")

@dp.message(DarsTaqsimot.teacher_count)
async def process_teacher_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Iltimos, to'g'ri o'qituvchilar sonini kiriting:")
        return
    
    count = int(message.text)
    await state.update_data(teacher_count=count, current_teacher=1, teachers=[])
    
    await state.set_state(DarsTaqsimot.teacher_name)
    await message.answer("<b>1-o'qituvchining F.I.Sh. (Familiyasi, Ismi, Sharifi)ni kiriting:</b>\n<i>(Masalan: Alimov Vali Karimovich)</i>", parse_mode="HTML")

@dp.message(DarsTaqsimot.teacher_name)
async def process_teacher_name(message: types.Message, state: FSMContext):
    t_name = message.text.strip()
    await state.update_data(current_teacher_name=t_name)
    
    data = await state.get_data()
    await ask_teacher_category(message, state, data['current_teacher'], t_name)

async def ask_teacher_category(event, state: FSMContext, teacher_num: int, teacher_name: str):
    data = await state.get_data()
    is_boshlangich = data['category'] == "boshlangich"

    buttons = [
        [InlineKeyboardButton(text="1. Oliy toifali o'qituvchi", callback_data="t_1")],
        [InlineKeyboardButton(text="2. Sertifikatli o'qituvchi (Milliy/Xalqaro)", callback_data="t_2")],
        [InlineKeyboardButton(text="3. Birinchi toifali o'qituvchi", callback_data="t_3")],
        [InlineKeyboardButton(text="4. Ikkinchi toifali o'qituvchi", callback_data="t_4")],
        [InlineKeyboardButton(text="5. Oliy ma'lumotli toifasiz", callback_data="t_5")],
        [InlineKeyboardButton(text="6. Qayta tayyorlash diplomli", callback_data="t_6")],
        [InlineKeyboardButton(text="7. O'rindosh o'qituvchi", callback_data="t_7")],
        [InlineKeyboardButton(text="8. OTM 3-4 kurs talabasi", callback_data="t_8")]
    ]
    
    if is_boshlangich:
        buttons.append([InlineKeyboardButton(text="9. O'rta maxsus (Professional)", callback_data="t_9")])
        
    buttons.append([InlineKeyboardButton(text="10. Rahbar xodim", callback_data="t_10")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    msg_text = f"<b>{teacher_name}</b> ning maqomi/toifasini tanlang:"
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(msg_text, parse_mode="HTML", reply_markup=kb)
    else:
        await event.answer(msg_text, parse_mode="HTML", reply_markup=kb)
    
    await state.set_state(DarsTaqsimot.teachers_data)

@dp.callback_query(DarsTaqsimot.teachers_data, F.data.startswith("t_"))
async def process_teacher_data(callback: types.CallbackQuery, state: FSMContext):
    step_num = int(callback.data.replace("t_", ""))
    data = await state.get_data()
    
    teachers = data['teachers']
    
    names = {
        1: "Oliy toifali",
        2: "Sertifikatli (Milliy/Xalqaro)",
        3: "1-toifali",
        4: "2-toifali",
        5: "Oliy ma'lumotli toifasiz",
        6: "Qayta tayyorlash diplomli",
        7: "O'rindosh o'qituvchi",
        8: "OTM talabasi",
        9: "O'rta maxsus (Professional)",
        10: "Rahbar xodim"
    }
    
    teachers.append({
        "id": data['current_teacher'],
        "fish": data['current_teacher_name'],
        "step": step_num,
        "status_name": names[step_num]
    })
    
    current = data['current_teacher']
    total_teachers = data['teacher_count']
    
    if current < total_teachers:
        next_num = current + 1
        await state.update_data(teachers=teachers, current_teacher=next_num)
        await state.set_state(DarsTaqsimot.teacher_name)
        await callback.message.edit_text(
            f"<b>{next_num}-o'qituvchining F.I.Sh. (Familiyasi, Ismi, Sharifi)ni kiriting:</b>", 
            parse_mode="HTML"
        )
    else:
        await calculate_and_show(callback.message, state, data, teachers)
    await callback.answer()

async def calculate_and_show(message: types.Message, state: FSMContext, data: dict, teachers: list):
    rate = data['rate'] # 18 yoki 20 soat
    max_rate = rate * 1.5 # 1.5 stavka (27 yoki 30 soat)
    total_hours = data['total_hours']
    
    # Rasmiy 10 ta ketma-ketlik bo'yicha saralash
    sorted_teachers = sorted(teachers, key=lambda x: x['step'])
    
    remaining_hours = total_hours
    results = []
    
    for t in sorted_teachers:
        if remaining_hours <= 0:
            assigned = 0
        else:
            if t['step'] in [1, 2, 3]: # Oliy, Sertifikatli, 1-toifa
                assigned = min(remaining_hours, max_rate)
            else: # Qolgan toifalar
                assigned = min(remaining_hours, rate)
            
            remaining_hours -= assigned
        
        results.append((t, assigned))
    
    res_text = (
        f"📊 <b>DARS TAQSIMOTI NATIJASI (RASMIY NIZOM BO'YICHA)</b>\n\n"
        f"🔹 <b>Fan:</b> {data['subject_name']}\n"
        f"🔹 <b>Jami dars soati:</b> {total_hours} soat\n"
        f"🔹 <b>1 stavka me'yori:</b> {rate} soat\n"
        f"🔹 <b>O'qituvchilar soni:</b> {len(teachers)} nafar\n\n"
        f"<b>Ustuvor ketma-ketlik bo'yicha taqsimot:</b>\n"
    )
    
    for idx, (t, h) in enumerate(results, 1):
        stavka = round(h / rate, 2)
        res_text += (
            f"\n<b>{idx}. {t['fish']}</b>\n"
            f" └ Maqomi: <i>{t['status_name']} ({t['step']}-o'rin)</i>\n"
            f" └ Dars soati: <b>{h} soat</b> ({stavka} stavka)\n"
        )
    
    if remaining_hours > 0:
        res_text += f"\n⚠️ <b>Eslatma:</b> Taqsimlanmay qolgan dars soati: <b>{remaining_hours} soat</b>."
    
    await message.answer(res_text, parse_mode="HTML", reply_markup=main_kb)
    await state.clear()

# Web server (Render uchun)
async def handle(request):
    return web.Response(text="Bot ishlayapti!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
