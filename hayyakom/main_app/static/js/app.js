const dateInput = document.getElementById('id_end_date');
if (dateInput) {
  flatpickr(dateInput, {
    dateFormat: "Y-m-d",
    altInput: true,
    altFormat: "F j, Y",
  });
}