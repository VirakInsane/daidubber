# JAI AUTO DUBBING - AI Chinese to Khmer Dubbing Suite 🎬⚡
កម្មវិធីស្វ័យប្រវត្តិកម្មសម្រាប់បញ្ចូលសំឡេងរឿង/វីដេអូចិនទៅជាភាសាខ្មែរ (Chinese ➔ Khmer Video Dubber)

---

## 🌟 លក្ខណៈពិសេសសំខាន់ៗ (Key Features)

1. **បំបែកសំឡេង (AI Vocal Separation with Demucs)**:
   - **រក្សាទុកភ្លេងខាងក្រោយ (BGM) & Sound Effects 100%**: លុបតែសំឡេងនិយាយដើមរបស់តួអង្គចិនចេញ។
   - ភ្លេងផ្ទៃក្រោយ សំឡេងកាប់ចាក់ ផ្ទុះ ឬបរិយាកាស (Ambience) នៅរក្សាបានច្បាស់ល្អដូចដើម។

2. **ការនិយាយត្រូវជាមួយសកម្មភាព មិនមានដាច់សំឡេង (Smart Audio Sync & Dynamic Time-Stretch)**:
   - ប្រើប្រាស់ **Whisper AI** លើ GPU CUDA ដើម្បីស្រង់ពេលវេលានិយាយ (Timestamps) ច្បាស់ដល់មីលីវិនាទី។
   - **Google Gemini AI** បកប្រែដោយកំណត់ប្រវែងប្រយោគឲ្យត្រូវនឹងថិរវេលាដើម (Duration-constrained natural film translation)។
   - **Dynamic Time-Stretching**: បត់បែនល្បឿននិយាយតាមក្បួនដោះស្រាយពិសេស ដែលធានាថា **សំឡេងមិនដាច់ពាក់កណ្តាល (No Cut-off)** និងមិនត្រួតស៊ីគ្នានឹងប្រយោគបន្ទាប់។

3. **ការ Render វីដេអូល្បឿនលឿនបំផុត (Ultra-Fast 3-Second Render)**:
   - ប្រើបច្ចេកវិទ្យា **Direct Stream Copy (`-c:v copy`)** របស់ FFmpeg ដោយមិនបាច់ Encode រូបភាពវីដេអូឡើងវិញឡើយ។
   - វីដេអូ 10 ទៅ 30 នាទី ចំណាយពេល Render ត្រឹមតែ **3 ទៅ 5 វិនាទី** ប៉ុណ្ណោះ!
   - គាំទ្រផងដែរនូវ **NVIDIA NVENC Hardware Acceleration** សម្រាប់អ្នកដែលចង់ Encode តាម GPU RTX 3070។

4. **ការរចនា UI ថ្មី បែប Cyberpunk Dark Glassmorphism**:
   - រចនាឡើងស្របតាមគំរូរូបភាពដែលអ្នកបានផ្តល់ជូន ប៉ុន្តែបន្ថែមភាពទាន់សម័យ កម្រិតពណ៌ និងប៊ូតុងភ្លឺរលោង (Neon Glow)។
   - បង្ហាញព័ត៌មានលម្អិត៖ ចំនួនវីដេអូសរុប, ចំនួនដែលបាន Dubbed រួច, និងចំនួននៅសល់។
   - បង្ហាញដំណាក់កាលដំណើរការ (Pipeline Progress Pills) ជាមួយផ្ទាំង Activity Logs ផ្ទាល់។

5. **សំឡេងខ្មែរ Neural TTS គុណភាពខ្ពស់**:
   - ប្រើប្រាស់សំឡេង **Microsoft Neural Khmer**:
     * `km-KH-PisethNeural` (សំឡេងប្រុស - Male Voice)
     * `km-KH-SreymomNeural` (សំឡេងស្រី - Female Voice)
     * មុខងារ **Auto Switch** ឆ្លាស់សំឡេងប្រុសស្រីស្វ័យប្រវត្តិតាមការសន្ទនា។

---

## 🚀 របៀបប្រើប្រាស់ (Quick Start)

### របៀបទី 1: ចុចដំណើរការតាម File `run.bat`
គ្រាន់តែចុចពីរដង (Double-click) លើ File [run.bat](file:///d:/project/AutoDaiDubber/run.bat) ដើម្បីបើកកម្មវិធីភ្លាមៗ។

### របៀបទី 2: ដំណើរការតាម Terminal / PowerShell
```powershell
python app.py
```

---

## 📋 ជំហានដំណើរការលើផ្ទាំង UI

1. **ជ្រើសរើស Folder វីដេអូដើម (CHOOSE FOLDER)**:
   - ចុចប៊ូតុង `📁 Browse` ដើម្បីជ្រើសរើស Folder ដែលផ្ទុកវីដេអូចិនរបស់អ្នក (ឧទាហរណ៍៖ `D:/video/origin/...`)។
   - កម្មវិធីនឹងរាប់ចំនួនវីដេអូដែលរកឃើញភ្លាមៗ។

2. **ជ្រើសរើស Folder សម្រាប់រក្សាទុក (FOLDER SAVED)**:
   - ចុចប៊ូតុង `📁 Browse` ជ្រើសរើសទីតាំងសម្រាប់ Save វីដេអូខ្មែរសម្រេច។

3. **ជ្រើសរើសរបៀបចាត់ចែងសំឡេងដើម (Audio Vocal Mode)**:
   - 🌟 **រក្សាភ្លេង BGM/Sound FX (លុបតែសំឡេងចិន)** *(ណែនាំ)*
   - 🔇 **Mute សំឡេងដើមទាំងអស់ (ដាក់តែសំឡេងខ្មែរ)**
   - 🔉 **Audio Ducking (បន្ថយសំឡេងដើម)**

4. **កំណត់ Gemini API Key (ចុចរូបតំណាងកង់ហ្វ្រាំង ⚙️)**:
   - ចុចប៊ូតុង **⚙️ Settings** នៅផ្នែកខាងលើស្តាំ។
   - បញ្ចូល **Gemini API Key** របស់អ្នក (យកបានឥតគិតថ្លៃពី [Google AI Studio](https://aistudio.google.com/app/apikey))។
   - ចុចប៊ូតុង `🔗 តេស្តភ្ជាប់ API` ដើម្បីផ្ទៀងផ្ទាត់។
   - ចុច `💾 រក្សាទុក (Save Settings)`។

5. **ចាប់ផ្តើម Dubbing**:
   - ចុចប៊ូតុងពណ៌ខៀវភ្លឺ **▶ Start Dubbing (ចាប់ផ្តើម)**។
   - កម្មវិធីនឹងដំណើរការតាមដំណាក់កាលស្វ័យប្រវត្តិទាំង 7 ដំណាក់កាល។
   - នៅពេលរួចរាល់ អាចចុច **📂 បើក Folder សម្រេច** ដើម្បីមើលវីដេអូភ្លាមៗ!

---

## 🛠️ រចនាសម្ព័ន្ធគម្រោង (Project Architecture)

```
AutoDaiDubber/
├── app.py                      # ច្រកចូលដើមសម្រាប់បើកកម្មវិធី (Entry Point)
├── run.bat                     # File Shortcut សម្រាប់ចុចបើកលើ Windows
├── config.json                 # ការកំណត់ដែលបានរក្សាទុក (Config Persistence)
├── requirements.txt            # បញ្ជី Libraries
├── README.md                   # ឯកសារណែនាំ
├── core/
│   ├── config_manager.py       # គ្រប់គ្រង Settings
│   ├── vocal_separator.py      # បំបែកសំឡេង BGM និង Vocal (Demucs GPU)
│   ├── transcriber.py          # សម្គាល់ពាក្យចិន & Timestamps (Whisper CUDA)
│   ├── translator.py           # បកប្រែជាភាសាខ្មែរតាមរឿងកុន (Gemini AI)
│   ├── tts_engine.py           # បង្កើតសំឡេងខ្មែរ (Microsoft Neural Edge-TTS)
│   ├── audio_sync.py           # តម្រឹមចង្វាក់, Time-Stretch និង Ducking (មិនដាច់សំឡេង)
│   ├── video_renderer.py       # Render វីដេអូល្បឿនលឿន (FFmpeg Fast Mux)
│   └── pipeline.py             # អ្នកសម្របសម្រួលដំណើរការទាំងមូល (Pipeline Orchestrator)
├── ui/
│   ├── main_window.py          # ផ្ទាំងកម្មវិធីធំ (MainWindow UI)
│   ├── settings_dialog.py      # ផ្ទាំងកំណត់ Settings (API Key & Models)
│   ├── components.py           # Components រចនាស្អាត (Cards, Pills, Console)
│   └── styles.py               # ពណ៌ Theme, Cyberpunk Glow & Fonts
└── utils/
    ├── file_utils.py           # ស្កេន Folder, រាប់ចំនួនភាគ, ពិនិត្យឈ្មោះ
    └── logger.py               # បង្ហាញព័ត៌មាន Log លើ Console និង UI
```
#   d a i d u b b e r  
 