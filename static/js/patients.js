let patients = [];

// تحميل قائمة المرضى
function loadPatients() {
  fetch("/api/patients", {
    headers: {
      Authorization: `Bearer ${getCookie("access_token_cookie")}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      patients = data;
      renderPatientsTable();
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("حدث خطأ في تحميل البيانات");
    });
}

// عرض البيانات في الجدول
function renderPatientsTable() {
  const tbody = document.getElementById("patientsTableBody");
  tbody.innerHTML = "";

  patients.forEach((patient, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${index + 1}</td>
            <td>${patient.full_name}</td>
            <td>${patient.gender || "-"}</td>
            <td>${patient.birth_date || "-"}</td>
            <td>${patient.phone_number || "-"}</td>
            <td>${patient.created_at ? new Date(patient.created_at).toLocaleDateString() : "-"}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="viewPatient(${patient.id})">
                    <i class="fas fa-eye"></i> عرض
                </button>
                <button class="btn btn-sm btn-warning" onclick="editPatient(${patient.id})">
                    <i class="fas fa-edit"></i> تعديل
                </button>
                <button class="btn btn-sm btn-danger" onclick="deletePatient(${patient.id})">
                    <i class="fas fa-trash"></i> حذف
                </button>
            </td>
        `;
    tbody.appendChild(row);
  });
}

// عرض نموذج إضافة مريض
function showAddPatientModal() {
  document.getElementById("modalTitle").textContent = "إضافة مريض جديد";
  document.getElementById("patientForm").reset();
  document.getElementById("patientId").value = "";

  const modal = new bootstrap.Modal(document.getElementById("patientModal"));
  modal.show();
}

// حفظ المريض (إضافة/تعديل)
function savePatient() {
  const patientId = document.getElementById("patientId").value;
  const url = patientId ? `/api/patients/${patientId}` : "/api/patients";
  const method = patientId ? "PUT" : "POST";

  const patientData = {
    first_name: document.getElementById("firstName").value,
    middle_name: document.getElementById("middleName").value,
    last_name: document.getElementById("lastName").value,
    gender: document.getElementById("gender").value,
    birth_date: document.getElementById("birthDate").value,
    phone_number: document.getElementById("phoneNumber").value,
  };

  fetch(url, {
    method: method,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getCookie("access_token_cookie")}`,
    },
    body: JSON.stringify(patientData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
        return;
      }

      alert(patientId ? "تم تحديث المريض بنجاح" : "تم إضافة المريض بنجاح");

      // إغلاق المودال وإعادة التحميل
      const modal = bootstrap.Modal.getInstance(
        document.getElementById("patientModal"),
      );
      modal.hide();
      loadPatients();
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("حدث خطأ في حفظ البيانات");
    });
}

// حذف المريض
function deletePatient(patientId) {
  if (!confirm("هل أنت متأكد من حذف هذا المريض؟")) {
    return;
  }

  fetch(`/api/patients/${patientId}`, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${getCookie("access_token_cookie")}`,
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
        return;
      }

      alert("تم حذف المريض بنجاح");
      loadPatients();
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("حدث خطأ في حذف المريض");
    });
}

// وظيفة مساعدة للحصول على الكوكيز
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

// تحميل البيانات عند فتح الصفحة
document.addEventListener("DOMContentLoaded", loadPatients);
