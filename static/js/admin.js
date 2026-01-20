function openAddProduct(){
    document.getElementById('add_product_popup').style.display = 'block';
}
function closeAddProduct(){
    document.getElementById('add_product_popup').style.display = 'none';
}
function openAddCategory(){
    document.getElementById('add_category_popup').style.display = 'block';
}
function closeAddCategory(){
    document.getElementById('add_category_popup').style.display = 'none';
}
function openAddBrand(){
    document.getElementById('add_brand_popup').style.display = 'block';
}
function closeAddBrand(){
    document.getElementById('add_brand_popup').style.display = 'none';
}

document.getElementById('add_product_form').addEventListener('submit', function(e){
    e.preventDefault();
    const formData = new FormData(this);

    fetch("{% url 'add_product' %}", {
        method: 'POST',
        headers: {
            'X-CSRFTOKEN': formData.get('csrfmiddlewaretoken')
        },
        body: formData
    })
    .then(response => {
        if(response.ok){
            alert('Added succesfully');
            closeAddProduct();
        }
        else{
            alert('Somethine went wrong');
        }
    })
})

document.addEventListener('DOMContentLoaded', function () {
    const selectAll = document.getElementById('select_all');
    const checkboxes = document.querySelectorAll('.row_checkbox');

    selectAll.addEventListener('change', function () {
        checkboxes.forEach(cb => cb.checked = this.checked);
    });

    function getSelectedIds() {
        return [...document.querySelectorAll('.row_checkbox:checked')]
            .map(cb => cb.closest('tr').getAttribute('data-id'));
    }

    document.getElementById('edit_btn').addEventListener('click', function () {
        const selected = getSelectedIds();
        console.log('Selected for edit:', selected);
    });

    document.getElementById('delete_btn').addEventListener('click', function () {
        const selected = getSelectedIds();
            if (selected.length === 0) {
                alert('No product selected.');
                return;
            }
        
            if (confirm(`Are you sure you want to delete ${selected.length} product(s)?`)) {
                fetch('/delete_products/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: JSON.stringify({ ids: selected }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        location.reload(); 
                    } else {
                        alert('Something went wrong.');
                    }
                });
            }    
    });
});
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
document.getElementById('edit_btn').addEventListener('click', function () {
    const selected = getSelectedIds();
    if (selected.length !== 1) {
        alert('Please select only one product to edit.');
        return;
    }

    const row = document.querySelector(`tr[data-id="${selected[0]}"]`);
    const id = selected[0];
    const name = row.querySelector('.prod_name').textContent;
    const stock = row.querySelector('.prod_stock').textContent;
    const price = row.querySelector('.prod_price').textContent;

    document.getElementById('edit_id').value = id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_stock').value = stock;
    document.getElementById('edit_price').value = price;

    document.getElementById('edit_product_popup').style.display = 'block';
});

function closeEditProduct() {
    document.getElementById('edit_product_popup').style.display = 'none';
}
document.getElementById('edit_form').addEventListener('submit', function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    fetch('/update_product/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Product updated!');
            location.reload();
        } else {
            alert('Failed to update.');
        }
    });
});
document.getElementById('delete_btn').addEventListener('click', function () {
    const selected = getSelectedIds();

    if (selected.length === 0) {
        alert('No products selected.');
        return;
    }

    if (!confirm('Are you sure you want to delete the selected products?')) return;

    fetch('/delete_products/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ ids: selected }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Deleted successfully!');
            location.reload();
        } else {
            alert('Failed to delete.');
        }
    });
});

function getSelectedIds() {
    const checkboxes = document.querySelectorAll('.row_checkbox');
    const ids = [];

    checkboxes.forEach((checkbox, index) => {
        if (checkbox.checked) {
            const row = checkbox.closest('tr');
            ids.push(row.getAttribute('data-id'));
        }
    });

    return ids;
}
document.getElementById('select_all').addEventListener('change', function () {
    const checkboxes = document.querySelectorAll('.row_checkbox');
    checkboxes.forEach(cb => cb.checked = this.checked);
});
