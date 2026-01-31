-- ===============================
-- USERS (System Users)
-- ===============================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'DOCTOR', 'ASSISTANT')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- PATIENTS (Basic Patient Info)
-- ===============================
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    birth_date DATE,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============================
-- MEDICAL PROFILES (One per Patient)
-- ===============================
CREATE TABLE medical_profiles (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    blood_type VARCHAR(3),        
    height INTEGER,
    weight FLOAT,
    chronic_diseases TEXT,
    allergies TEXT,
    general_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_medical_profile_patient
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);

-- ===============================
-- MEDICAL CASES (Disease / Visit History)
-- ===============================
CREATE TABLE medical_cases (
    id SERIAL PRIMARY KEY,

    medical_profile_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,

    case_date DATE NOT NULL,                -- تاريخ الإصابة / الزيارة
    case_description TEXT,                  -- تفاصيل الحالة
    treatment_details TEXT,                 -- العلاج
    prescribed_medications TEXT,            -- الأدوية (نصي)
    lab_tests_and_results TEXT,              -- التحاليل ونتائجها
    visited_facilities TEXT,                -- مشافي / مراكز صحية
    additional_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_case_profile
        FOREIGN KEY (medical_profile_id)
        REFERENCES medical_profiles(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_case_doctor
        FOREIGN KEY (doctor_id)
        REFERENCES users(id)
        ON DELETE RESTRICT
);


-- إضافة المستخدمين التجريبيين
INSERT INTO users (full_name, username, password_hash, role, is_active) VALUES
('مدير النظام', 'admin', '$2b$12$3lVpB4oQnR7VJ9VQ8Z5Y5uP9V7sA6B8C9D0E1F2G3H4I5J6K7L8M9N0O1P', 'ADMIN', true),
('دكتور أحمد محمد', 'doctor1', '$2b$12$3lVpB4oQnR7VJ9VQ8Z5Y5uP9V7sA6B8C9D0E1F2G3H4I5J6K7L8M9N0O1P', 'DOCTOR', true),
('مساعد إكلينيكي', 'assistant1', '$2b$12$3lVpB4oQnR7VJ9VQ8Z5Y5uP9V7sA6B8C9D0E1F2G3H4I5J6K7L8M9N0O1P', 'ASSISTANT', true);

-- ملاحظة: كلمة المرور لجميعهم هي "password123"

-- إضافة المرضى التجريبيين
INSERT INTO patients (first_name, middle_name, last_name, gender, birth_date, phone_number, created_at) VALUES
('محمد', 'عبدالله', 'الزيد', 'ذكر', '1993-05-15', '0501234567', NOW()),
('سارة', 'علي', 'العتيبي', 'أنثى', '1998-08-22', '0557654321', NOW()),
('خالد', 'سالم', 'العمري', 'ذكر', '1983-12-10', '0567890123', NOW()),
('فاطمة', 'يوسف', 'الشهري', 'أنثى', '1990-03-30', '0543210987', NOW()),
('علي', 'محمد', 'الحارثي', 'ذكر', '1978-07-18', '0534567890', NOW());

-- الحصول على أرقام المرضى المضافة
SELECT id, first_name, last_name FROM patients;


-- إضافة الملفات الطبية للمرضى
INSERT INTO medical_profiles (patient_id, blood_type, height, weight, chronic_diseases, allergies, general_notes, created_at) VALUES
(1, 'O+', 175, 72.5, 'لا يوجد', 'حساسية البنسلين', 'مريض منتظم في المراجعات', NOW()),
(2, 'A+', 162, 58.0, 'سكري نوع 2', 'لا يوجد', 'تأخذ الأنسولين بانتظام', NOW()),
(3, 'B+', 180, 85.0, 'ضغط الدم', 'لا يوجد', 'يحتاج مراقبة ضغط الدم يومياً', NOW()),
(4, 'AB+', 155, 52.0, 'ربو', 'حساسية الغبار', 'تستخدم بخاخ الربو', NOW()),
(5, 'O-', 170, 68.0, 'لا يوجد', 'لا يوجد', 'صحة جيدة', NOW());


-- الحصول على أرقام الملفات الطبية والأطباء
SELECT mp.id as profile_id, u.id as doctor_id 
FROM medical_profiles mp, users u 
WHERE u.username = 'doctor1';

-- إضافة الحالات المرضية
INSERT INTO medical_cases (medical_profile_id, doctor_id, case_date, case_description, treatment_details, prescribed_medications, lab_tests_and_results, visited_facilities, additional_notes, created_at) VALUES
-- الحالات لمحمد
(1, 2, '2024-01-10', 'نزلة برد شديدة مع ارتفاع في درجة الحرارة', 'راحة تامة، سوائل، خافض للحرارة', 'باراسيتامول 500mg كل 6 ساعات، فيتامين سي', 'تحليل دم - ارتفاع بسيط في كريات الدم البيضاء', 'عيادة الأسرة', 'تحسن بعد 3 أيام من العلاج', NOW()),

(1, 2, '2024-03-15', 'آلام في الظهر نتيجة حمل أثقال', 'علاج طبيعي، كمادات دافئة', 'ايبوبروفين 400mg عند اللزوم، مرهم كريم', 'أشعة سينية - لا كسور', 'مركز العلاج الطبيعي', 'نصح بعدم حمل الأثقال لمدة أسبوعين', NOW()),

-- الحالات لسارة
(2, 2, '2024-02-05', 'فحص دوري لمريضة السكري', 'ضبط مستوى السكر، نصائح غذائية', 'ميتفورمين 850mg مرتين يومياً', 'سكر تراكمي 7.2% - يحتاج تحسين', 'عيادة السكري', 'نصح بممارسة رياضة خفيفة يومياً', NOW()),

-- الحالات لخالد
(3, 2, '2024-01-20', 'ارتفاع ضغط الدم', 'نظام غذائي قليل الملح، متابعة الضغط', 'لوزارتان 50mg يومياً', 'ضغط الدم 150/95 - مرتفع', 'عيادة القلب', 'يحتاج قياس ضغط الدم يومياً وتسجيل القراءات', NOW()),

(3, 2, '2024-04-10', 'دوار وإرهاق', 'فحص شامل، تحاليل دم', 'مكملات حديد، فيتامين ب12', 'نقص فيتامين ب12، فقر دم بسيط', 'المختبر الطبي', 'تحسن ملحوظ بعد أسبوعين من العلاج', NOW()),

-- الحالات لفاطمة
(4, 2, '2024-03-01', 'نوبة ربو', 'أكسجين، بخاخات موسعة للشعب', 'فنتولين بخاخ، كورتيكوستيرويد', 'قياس وظائف الرئة - انخفاض بنسبة 30%', 'قسم الطوارئ', 'نصح بتجنب المثيرات للربو', NOW()),

-- الحالات لعلي
(5, 2, '2024-02-28', 'فحص دوري شامل', 'فحص طبي كامل', 'فيتامين د 1000 وحدة يومياً', 'جميع التحاليل طبيعية، نقص فيتامين د بسيط', 'العيادة العامة', 'صحة جيدة، موعد مراجعة خلال 6 أشهر', NOW());




-- سكريبت SQL كامل لتحديث كلمات المرور
-- كلمة المرور "password123" مشفرة باستخدام werkzeug

-- 1. محو كلمات المرور القديمة غير المشفرة
UPDATE users SET password_hash = NULL;

-- 2. إضافة كلمات المرور المشفرة الجديدة
UPDATE users SET password_hash = '$2b$12$G2lvem5uhOP.BuJW3wgtC.YR/KcnyEeTE8UapKIXYgj8UwL/30Ro2' WHERE username = 'admin';
UPDATE users SET password_hash = '$2b$12$G2lvem5uhOP.BuJW3wgtC.YR/KcnyEeTE8UapKIXYgj8UwL/30Ro2' WHERE username = 'doctor1';
UPDATE users SET password_hash = '$2b$12$G2lvem5uhOP.BuJW3wgtC.YR/KcnyEeTE8UapKIXYgj8UwL/30Ro2' WHERE username = 'assistant1';

-- 3. التحقق
SELECT 
    id, 
    username, 
    full_name,
    role,
    CASE 
        WHEN password_hash IS NULL THEN ' غير مشفر'
        WHEN LENGTH(password_hash) > 50 THEN ' مشفر'
        ELSE '  مشكوك فيه'
    END as password_status
FROM users;


    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

-- 1. إنشاء جدول المواعيد
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    appointment_type VARCHAR(100) DEFAULT 'عام',
    status VARCHAR(50) DEFAULT 'مجدول' CHECK (status IN ('مجدول', 'تم الحضور', 'ملغي', 'لم يحضر')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- المفاتيح الخارجية
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 2. إنشاء الفهارس لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- 3. إنشاء دالة لتحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 4. إنشاء trigger لتحديث updated_at
CREATE TRIGGER update_appointments_updated_at 
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. إضافة تعليق على الجدول
COMMENT ON TABLE appointments IS 'جدول إدارة مواعيد المرضى';
COMMENT ON COLUMN appointments.status IS 'حالة الموعد: مجدول، تم الحضور، ملغي، لم يحضر';
COMMENT ON COLUMN appointments.appointment_type IS 'نوع الموعد: عام، متابعة، كشف جديد، تحاليل، أشعة، طوارئ';
SELECT id, full_name FROM users WHERE role = 'DOCTOR' LIMIT 5;

-- 1. إدخال مواعيد تجريبية
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, duration_minutes, appointment_type, status, notes) VALUES
-- موعد 1
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE + INTERVAL '2 days',
    '09:00:00',
    30,
    'كشف جديد',
    'مجدول',
    'كشف أولي للمريض'
),

-- موعد 2
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE + INTERVAL '3 days',
    '10:30:00',
    45,
    'متابعة',
    'مجدول',
    'متابعة حالة سابقة'
),

-- موعد 3
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE + INTERVAL '1 days',
    '14:00:00',
    60,
    'تحاليل',
    'مجدول',
    'مراجعة نتائج التحاليل'
),

-- موعد 4 (في الماضي - تم الحضور)
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE - INTERVAL '2 days',
    '11:00:00',
    30,
    'عام',
    'تم الحضور',
    'تم إجراء الكشف وكتابة الوصفة'
),

-- موعد 5 (في الماضي - ملغي)
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE - INTERVAL '1 days',
    '15:30:00',
    30,
    'متابعة',
    'ملغي',
    'ألغى المريض بسبب ظروف طارئة'
),

-- موعد 6 (موعد اليوم)
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE,
    '16:00:00',
    45,
    'أشعة',
    'مجدول',
    'مراجعة صور الأشعة'
),

-- موعد 7 (الأسبوع القادم)
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE + INTERVAL '7 days',
    '08:30:00',
    30,
    'طوارئ',
    'مجدول',
    'حالة طارئة'
),

-- موعد 8 (لم يحضر)
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE - INTERVAL '3 days',
    '13:00:00',
    30,
    'عام',
    'لم يحضر',
    'المريض لم يحضر للموعد'
),

-- موعد 9
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE + INTERVAL '4 days',
    '09:45:00',
    60,
    'كشف جديد',
    'مجدول',
    'استشارة طبية شاملة'
),

-- موعد 10
(
    (SELECT id FROM patients ORDER BY RANDOM() LIMIT 1),
    (SELECT id FROM users WHERE role = 'DOCTOR' ORDER BY RANDOM() LIMIT 1),
    CURRENT_DATE + INTERVAL '5 days',
    '12:15:00',
    30,
    'متابعة',
    'مجدول',
    NULL
)
RETURNING *;



-- لإدخال بيانات تجريبية محددة (بعد معرفة IDs الحقيقية)
-- استبدل patient_id و doctor_id بالقيم الحقيقية من قاعدة البيانات

INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, duration_minutes, appointment_type, status, notes) VALUES
-- مواعيد لليوم والغد
(1, 2, CURRENT_DATE, '10:00:00', 30, 'كشف جديد', 'مجدول', 'أول زيارة للمريض'),
(2, 2, CURRENT_DATE, '11:00:00', 45, 'متابعة', 'مجدول', 'متابعة علاج الضغط'),
(3, 2, CURRENT_DATE, '14:00:00', 30, 'تحاليل', 'مجدول', 'مراجعة سكري'),
(4, 2, CURRENT_DATE + 1, '09:30:00', 60, 'كشف جديد', 'مجدول', 'فحص دوري'),
(5, 2, CURRENT_DATE + 1, '11:15:00', 30, 'متابعة', 'مجدول', 'متابعة علاج الربو'),

-- مواعيد الأسبوع القادم
(1, 2, CURRENT_DATE + 7, '10:00:00', 30, 'متابعة', 'مجدول', 'المتابعة الدورية'),
(2, 2, CURRENT_DATE + 7, '14:30:00', 45, 'أشعة', 'مجدول', 'أشعة على الصدر'),
(3, 2, CURRENT_DATE + 8, '08:45:00', 30, 'متابعة', 'مجدول', NULL),
(4, 2, CURRENT_DATE + 8, '12:00:00', 60, 'طوارئ', 'مجدول', 'شكوى حادة'),
(5, 2, CURRENT_DATE + 9, '15:00:00', 30, 'عام', 'مجدول', 'مراجعة نهائية'),

-- مواعيد سابقة
(1, 2, CURRENT_DATE - 7, '10:00:00', 30, 'كشف جديد', 'تم الحضور', 'تم التشخيص وكتابة العلاج'),
(2, 2, CURRENT_DATE - 5, '11:00:00', 45, 'متابعة', 'تم الحضور', 'تحسن في الحالة'),
(3, 2, CURRENT_DATE - 3, '14:00:00', 30, 'عام', 'ملغي', 'ألغى المريض'),
(4, 2, CURRENT_DATE - 2, '09:30:00', 60, 'كشف جديد', 'لم يحضر', 'لم يحضر المريض'),
(5, 2, CURRENT_DATE - 1, '16:00:00', 30, 'متابعة', 'تم الحضور', 'استكمال العلاج')
RETURNING *;
