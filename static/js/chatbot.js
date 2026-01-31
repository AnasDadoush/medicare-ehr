// static/js/chatbot.js
document.addEventListener("DOMContentLoaded", function () {
  // عناصر Chatbot
  const chatbotButton = document.getElementById("chatbot-toggle");
  const chatbotContainer = document.getElementById("chatbot-container");
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const sendButton = document.getElementById("send-button");
  const closeButton = document.getElementById("close-chatbot");

  // قائمة الأسئلة المتوقعة
  const commonQuestions = {
    "السلام عليكم":
      "وعليكم السلام ورحمة الله وبركاته، كيف يمكنني مساعدتك اليوم؟",
    مرحبا: "مرحباً بك! كيف يمكنني مساعدتك في نظام MediCare؟",
    "كيف أضيف مريض جديد":
      'لإضافة مريض جديد، انقر على "المرضى" في الشريط الجانبي ثم "إضافة مريض جديد".',
    "كيف أرى تقرير مريض":
      "لرؤية تقرير المريض، اذهب إلى صفحة المرضى وانقر على أيقونة العين بجوار المريض.",
    "ما هي الحالات المرضية":
      'الحالات المرضية هي زيارات المرضى للأطباء. يمكنك إضافتها من قسم "الحالات المرضية".',
    "كيف أسجل حالة مرضية":
      'لإضافة حالة مرضية، اذهب إلى قسم "الحالات المرضية" ثم انقر على "إضافة حالة مرضية".',
    شكرا: "العفو، أنا هنا لمساعدتك! إذا كان لديك أي أسئلة أخرى، لا تتردد في سؤالي.",
    مساعدة:
      "يمكنني مساعدتك في: 1- إضافة مرضى 2- عرض تقارير المرضى 3- إدارة الحالات المرضية 4- إنشاء تقارير",
    المواعيد:
      'للوصول إلى المواعيد: 1- انقر على "المواعيد" في الشريط الجانبي 2- لعرض التقويم: انقر على "عرض التقويم" 3- لإضافة موعد جديد: انقر على "إضافة موعد جديد"',
  };

  // قاعدة المعرفة الطبية
  const medicalKnowledge = {
    "ضغط الدم الطبيعي": "ضغط الدم الطبيعي للبالغين هو 120/80 ملم زئبق.",
    "مؤشر كتلة الجسم":
      "مؤشر كتلة الجسم (BMI) = الوزن (كجم) ÷ (الطول (متر) × الطول (متر)).",
    "السكر الطبيعي":
      "السكر الطبيعي الصائم: 70-100 ملجم/ديسيلتر، بعد الأكل: أقل من 140 ملجم/ديسيلتر.",
    الكوليسترول: "الكوليسترول الكلي المطلوب: أقل من 200 ملجم/ديسيلتر.",
    "نصائح صحية":
      "1- اشرب 8 أكواب ماء يومياً 2- مارس الرياضة 30 دقيقة يومياً 3- تناول الخضروات والفواكه",
  };

  // فتح/إغلاق Chatbot
  chatbotButton?.addEventListener("click", toggleChatbot);
  closeButton?.addEventListener("click", toggleChatbot);

  // إرسال رسالة عند الضغط على Enter
  chatInput?.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  // إرسال رسالة عند النقر على زر الإرسال
  sendButton?.addEventListener("click", sendMessage);

  function toggleChatbot() {
    chatbotContainer.classList.toggle("active");
    if (chatbotContainer.classList.contains("active")) {
      chatInput.focus();
    }
  }

  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // إضافة رسالة المستخدم
    addMessage(message, "user");
    chatInput.value = "";

    // معالجة الرسالة وإضافة رد
    setTimeout(() => {
      const response = getResponse(message);
      addMessage(response, "bot");
    }, 500);
  }

  function addMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const messageText = document.createElement("div");
    messageText.className = "message-text";
    messageText.textContent = text;

    const messageTime = document.createElement("div");
    messageTime.className = "message-time";
    messageTime.textContent = new Date().toLocaleTimeString("ar-SA", {
      hour: "2-digit",
      minute: "2-digit",
    });

    messageDiv.appendChild(messageText);
    messageDiv.appendChild(messageTime);
    chatMessages.appendChild(messageDiv);

    // التمرير إلى الأسفل
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function getResponse(message) {
    const msg = message.toLowerCase();

    // التحقق من الأسئلة الشائعة
    for (const [question, answer] of Object.entries(commonQuestions)) {
      if (msg.includes(question.toLowerCase())) {
        return answer;
      }
    }

    // التحقق من المعرفة الطبية
    for (const [topic, info] of Object.entries(medicalKnowledge)) {
      if (msg.includes(topic.toLowerCase())) {
        return info;
      }
    }

    // رد افتراضي
    const responses = [
      "أنا هنا لمساعدتك في نظام MediCare. يمكنك سؤالي عن: المرضى، الحالات المرضية، التقارير.",
      "عذراً، لم أفهم سؤالك. يمكنك محاولة صياغته بشكل آخر أو سؤالي عن: كيف أضيف مريض، كيف أرى التقارير.",
      "هل تقصد السؤال عن المرضى، الحالات المرضية، أو شيء آخر؟",
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }

  // إضافة رسالة ترحيبية
  if (chatMessages.children.length === 0) {
    setTimeout(() => {
      addMessage(
        "مرحباً! أنا مساعد MediCare. كيف يمكنني مساعدتك اليوم؟",
        "bot",
      );
    }, 1000);
  }
});
