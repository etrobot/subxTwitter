document.querySelectorAll('button.subx').forEach(function(button) {
  button.addEventListener('click', function(event) {
//    console.log(this.value);
    event.preventDefault();
    document.querySelector('input[name="target_id"]').value = this.value;
  });
});
var subscribeForm = document.getElementById('subscribe-form');
if (subscribeForm !== null) {

    subscribeForm.addEventListener('submit', function (event) {
      // 阻止表单的默认提交行为
      event.preventDefault();

      // 获取当前日期对象
      var currentDate = new Date();

      // 获取用户选择的时间
      var mailTimeValue = document.getElementById('mail-time').value;

      // 将用户选择的时间与当前日期拼接成一个字符串
      var selectedDateTimeString = currentDate.toISOString().slice(0, 10) + 'T' + mailTimeValue;
      // 将拼接后的字符串转换为时间戳
      var selectedDateTimeTimestamp = new Date(selectedDateTimeString).getTime() / 1000;

      // 判断 selectedDateTimeTimestamp 是否小于当前时间
      if (selectedDateTimeTimestamp <  currentDate.getTime() / 1000 - 5 * 60) {
        // 如果是，则增加一天
        selectedDateTimeTimestamp += 24 * 60 * 60; // 24小时 * 60分钟 * 60秒
      }
//      console.log(currentDate.getTime() / 1000)
//      console.log(selectedDateTimeString)
      // 将增加一天后的时间戳设置到隐藏的 input 元素中
      document.getElementById('mail-time-timestamp').value = selectedDateTimeTimestamp;

      // 提交表单
      this.submit();
    });
}
    var userLang = navigator.language || navigator.userLanguage;
    if (userLang.startsWith('en-')) {
          userLang = 'en';
        }
    var emailInput = document.querySelector('input[name="email"]');
    var targetIdInput = document.querySelector('input[name="target_id"]');
    var timeLabel = document.getElementById("time-label");
    var subscribeBtn = document.getElementById("subscribe-btn");
    var languageSelect = document.getElementById("language-select");
    var themeToggle = document.getElementById("theme-toggle");
    var body = document.body;

    // 检测浏览器或系统是否处于深色主题模式
    function isDarkTheme() {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // 浏览器或系统处于深色主题模式
        return true;
      } else {
        // 浏览器或系统处于浅色主题模式
        return false;
      }
    }

    // Toggle theme function
    themeToggle.addEventListener("click", function () {
      body.classList.toggle("dark");
      if (body.classList.contains("dark")) {
        themeToggle.textContent = "☀";
      } else {
        themeToggle.textContent = "️🌒";
      }
    });

    // 根据系统主题模式切换初始主题
    if (isDarkTheme()) {
      body.classList.add("dark");
      themeToggle.textContent = "☀";
    } else {
      body.classList.remove("dark");
      themeToggle.textContent = "️🌒";
    }

const languageData = {
         "columns": ["emailPlaceholder", "targetIdPlaceholder", "timeLabel", "subscribeBtn", "title"],
         "zh-CN": ["请输入您的邮箱", "请输入目标列表ID", "每日推送时间", "订阅/更新设定", "Twitter列表的GPT订阅"],
         "en": ["Enter your email", "Enter target list ID", "Daily Push Time", "Subscribe / Update Setting", "GPT Subscription for Twitter List"],
         "th": ["ใส่อีเมลของคุณ", "ใส่รหัสรายการเป้าหมาย", "เวลาการส่งประจำวัน", "สมัครสมาชิก / อัปเดตการตั้งค่า", "การสมัครสมาชิก GPT สำหรับรายการ Twitter"],
         "zh-TW": ["請輸入您的電子郵件", "請輸入目標列表ID", "每日推送時間", "訂閱/更新設定", "Twitter列表的GPT訂閱"],
         "ja": ["メールを入力してください", "ターゲットリストIDを入力してください", "デイリープッシュ時間", "購読/更新設定", "TwitterリストのGPTサブスクリプション"],
         "ko": ["이메일 를 입력하세요", "대상 목록 ID를 입력하세요", "매일 푸시 시간", "구독/업데이트 설정", "Twitter 목록을 위한 GPT 구독"],
         "es": ["Ingrese su correo electrónico", "Ingrese el ID de la lista de destino", "Hora de envío diario", "Suscribirse / Actualizar configuración", "Suscripción GPT para la lista de Twitter"],
         "pt": ["Digite seu de e-mail", "Digite o ID da lista de destino", "Horário de envio diário", "Inscrever-se / Atualizar configuração", "Assinatura GPT para Lista do Twitter"],
         "de": ["Geben Sie Ihre E-Mail ein", "Geben Sie die Ziellisten-ID ein", "Tägliche Push-Zeit", "Abonnieren / Aktualisieren der Einstellung", "GPT-Abonnement für Twitter-Liste"],
         "fr": ["Entrez votre e-mail", "Entrez l'identifiant de la liste cible", "Heure d'envoi quotidienne", "S'abonner / Mettre à jour la configuration", "Abonnement GPT pour la liste Twitter"],
         "ar": ["أدخل بريدك الإلكتروني", "أدخل معرف قائمة الهدف", "وقت الدفع اليومي", "الاشتراك / تحديث الإعداد","اشتراك GPT لقائمة تويتر"],
         "id": ["Masukkan email Anda", "Masukkan ID daftar target", "Waktu Dorong Harian", "Berlangganan / Perbarui Pengaturan", "Langganan GPT untuk Daftar Twitter"],
         "ms": ["Masukkan emel anda", "Masukkan ID senarai sasaran", "Masa Dorong Harian", "Langgan / Kemas kini Tetapan", "Langganan GPT untuk Senarai Twitter"],
         "tl": ["Maglagay ng iyong email", "Maglagay ng ID ng target list", "Araw-araw na Oras ng Pag-push", "Mag-subscribe / Mag-update ng Oras", "GPT Subscription para sa Twitter List"],
         "vi": ["Nhập email của bạn", "Nhập ID danh sách mục tiêu", "Thời gian đẩy hàng hàng ngày", "Đăng ký / Cập nhật cài đặt", "Đăng ký GPT cho Danh sách Twitter"],
         "pl": ["Wprowadź swój adres e-mail", "Wprowadź identyfikator listy docelowej", "Codzienny czas wysyłki", "Zapisz się / Zaktualizuj ustawienia", "Subskrypcja GPT dla listy Twitter"],
         "nl": ["Voer uw e-mailadres in", "Voer de doellijst-ID in", "Dagelijkse Push-tijd", "Inschrijven / Bijwerken Instelling", "GPT-abonnement voor Twitter-lijst"]
    };
    // Function to set placeholders and titles based on language
    function setLanguage(selectedLanguage) {
     const placeholders = languageData.columns.reduce((acc, column) => {
    if (languageData[selectedLanguage]) {
      acc[column] = languageData[selectedLanguage][languageData.columns.indexOf(column)];
    } else {
      acc[column] = "Placeholder not found";
    }
    return acc;
  }, {});
     emailInput.placeholder = placeholders.emailPlaceholder;
     targetIdInput.placeholder = placeholders.targetIdPlaceholder;
     timeLabel.textContent = placeholders.timeLabel;
     subscribeBtn.textContent = placeholders.subscribeBtn;
     document.getElementById("title").textContent = placeholders.title;
}

    // Initial set of placeholders and titles

    setLanguage(userLang);
    document.getElementById('language-select').value=userLang
    var defaultLanguageInput = document.getElementById("current-language");
    defaultLanguageInput.value = userLang;

    // Toggle language function
    languageSelect.addEventListener("change", function () {
      var selectedLanguage = languageSelect.value;
      setLanguage(selectedLanguage);
      // 更新隐藏 input 的值
      var currentLanguageInput = document.getElementById("current-language");
      currentLanguageInput.value = selectedLanguage;
    });