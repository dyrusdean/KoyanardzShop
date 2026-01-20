/* Product */
    document.addEventListener('DOMContentLoaded', function () {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');

        const cartButtons = document.querySelectorAll('.add-to-cart-btn');

        cartButtons.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();

                const productId = this.dataset.productId;

                fetch(`/add-to-cart/${productId}`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ quantity: 1 })
                })
                .then(response => response.json())
                .then(data => {
                    const cartCountElement = document.getElementById('cart-count');
                    if (cartCountElement) {
                        cartCountElement.textContent = data.cart_count;
                    }

                    const popup = document.getElementById('cart-popup');
                    if (popup) {
                        popup.classList.add('show');
                        setTimeout(() => popup.classList.remove('show'), 2200);
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    });

/* Carousel Item */
    (function(){
        const slider = document.querySelector('.checkout_slider');
        const slides = document.querySelectorAll('.checkout_left');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');

        if (!slider || slides.length === 0 || !prevBtn || !nextBtn) {
            // Carousel not present on this page — skip initialization
            return;
        }

        let currentIndex = 0;

        function updateSlider() {
            if (!slider) return;
            slider.style.transform = `translateX(-${currentIndex * 100}%)`;
        }

        nextBtn.addEventListener('click', () => {
            if (currentIndex < slides.length - 1) {
                currentIndex++;
                updateSlider();
            }
        });

        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateSlider();
            }
        });

        updateSlider();
    })();

/* Favorites */
/* Favorites: event delegation handles clicks on favorite buttons and dropdown remove buttons */
document.addEventListener('click', function (e) {
    // Debug: Log all clicks on product cards to see if events reach here
    if (e.target.closest('.product-card') || e.target.closest('.favorite_btn')) {
        console.log('📍 Click detected on product-card/favorite_btn:', {
            target: e.target,
            targetClass: e.target.className,
            targetTag: e.target.tagName,
            button: e.target.closest('.favorite_btn')
        });
    }
    
    // Favorite button on product cards
    let favBtn = e.target;
    
    // Check if clicked element is the icon inside the button
    if (favBtn && favBtn.tagName === 'I' && favBtn.parentElement && favBtn.parentElement.classList.contains('favorite_btn')) {
        favBtn = favBtn.parentElement;
    }
    
    // Check if element has the class directly
    if (favBtn && favBtn.classList && favBtn.classList.contains('favorite_btn')) {
        console.log('❤️ Favorite button clicked');
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        const productId = favBtn.getAttribute('data-product-id');
        console.log('Product ID:', productId);

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');
        console.log('CSRF Token:', csrftoken);

        fetch(`/toggle_favorite/${productId}/`, {
            method: 'POST',
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({})
        })
        .then(res => {
            console.log('Response status:', res.status, res.ok);
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            const dropdown = document.getElementById('favoriteDropdown');
            console.log('✅ toggle_favorite response:', data);

            // If server provides authoritative dropdown HTML, replace it and return
            if (data.dropdown_html && dropdown) {
                dropdown.innerHTML = data.dropdown_html;
            }

            if (data.status === 'added') {
                favBtn.classList.add('favorited');
                
                // Change heart icon from outline to solid
                const icon = favBtn.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-regular');
                    icon.classList.add('fa-solid');
                }

                // If no full dropdown was provided, try inserting the returned single-item HTML
                if (!data.dropdown_html && data.html && dropdown) {
                    if (!dropdown.querySelector(`.fav-item[data-product-id="${data.product.id}"]`)) {
                        dropdown.insertAdjacentHTML('afterbegin', data.html);
                    }
                }

                // Fallback: create minimal DOM from product payload
                if (!data.dropdown_html && !data.html && data.product && dropdown) {
                    if (!dropdown.querySelector(`.fav-item[data-product-id="${data.product.id}"]`)) {
                        const item = document.createElement('div');
                        item.className = 'fav-item';
                        item.setAttribute('data-product-id', data.product.id);
                        item.innerHTML = `
                            <a href="/product/${data.product.id}/"><img src="${data.product.img || ''}" alt="${data.product.name}" width="40" height="40"></a>
                            <div class="fav-meta">${data.product.name}</div>
                            <div class="fav-actions"><button type="button" class="fav-remove-btn" data-product-id="${data.product.id}" aria-label="Remove from favorites"><i class="fa-solid fa-trash" aria-hidden="true"></i></button></div>
                        `;
                        dropdown.prepend(item);
                    }
                }
            } else if (data.status === 'removed') {
                favBtn.classList.remove('favorited');
                
                // Change heart icon from solid to outline
                const icon = favBtn.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-solid');
                    icon.classList.add('fa-regular');
                }

                // If server didn't return full dropdown HTML, remove the specific item from DOM
                if (!data.dropdown_html) {
                    if (dropdown) {
                        const card = dropdown.querySelector(`.fav-item[data-product-id="${productId}"]`);
                        if (card) card.remove();
                    }
                }

                // Remove card on favorites page if present
                const favCard = favBtn.closest('.favorites');
                if (favCard) favCard.remove();

                // Update any product-card favorite button states
                const productCard = favBtn.closest('.product-card');
                if (productCard) {
                    const prodBtn = productCard.querySelector(`.favorite_btn[data-product-id="${productId}"]`);
                    if (prodBtn) prodBtn.classList.remove('favorited');
                }
            }
        })
        .catch(err => {
            console.error('❌ Error toggling favorite:', err);
        });
    }

    // Remove button inside favorites dropdown
    const removeBtn = e.target.closest && e.target.closest('.fav-remove-btn');
    if (removeBtn) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        const productId = removeBtn.getAttribute('data-product-id');

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');

        fetch(`/toggle_favorite/${productId}/`, {
            method: 'POST',
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({})
        })
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            console.debug('remove favorite response', data);
            // If server returned a full dropdown, replace it
            const dropdown = document.getElementById('favoriteDropdown');
            if (data.dropdown_html && dropdown) {
                dropdown.innerHTML = data.dropdown_html;
            } else if (data.status === 'removed') {
                const item = removeBtn.closest('.fav-item');
                if (item) item.remove();

                // update any product card favorite state
                const prodBtn = document.querySelector(`.favorite_btn[data-product-id="${productId}"]`);
                if (prodBtn) {
                    prodBtn.classList.remove('favorited');
                    const icon = prodBtn.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fa-solid');
                        icon.classList.add('fa-regular');
                    }
                }
            }
        })
        .catch(err => console.error('Error removing favorite from dropdown:', err));
    }
});


/* Appointment */
document.addEventListener('DOMContentLoaded', function() {
    let calendarEl = document.getElementById('calendar');
    let calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/appointments/json/',
        eventColor: '#0b7285'
    });
    calendar.render();
});

/* AIBOT */
function sendMessage() {
    var userMessage = document.getElementById('ai_input').value;
    var chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += '<div class="message"><strong>You:</strong> ' + userMessage + '</div>';

    fetch('/intent/?message=' + encodeURIComponent(userMessage))
        .then(response => response.json())
        .then(data => {
            chatbox.innerHTML += '<div class="aibot_message"><strong>Bot:</strong> ' + data.reply + '</div>';
            document.getElementById('ai_input').value = '';
        });
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('ai_input').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
});

/* Favorite button click handler with multiple event types for maximum compatibility */
document.addEventListener('mousedown', function(e) {
    // Try to find the button - check if target is the button or a child of the button
    let btn = e.target.closest('button.favorite_btn[data-product-id]');
    
    if (btn) {
        console.log('✅ FAVORITE BUTTON MOUSEDOWN:', btn, 'Product ID:', btn.getAttribute('data-product-id'));
        e.preventDefault();
        e.stopPropagation();
    }
}, true); // Capture phase

document.addEventListener('click', function(e) {
    // Try to find the button - check if target is the button or a child of the button
    let btn = e.target.closest('button.favorite_btn[data-product-id]');
    
    if (btn) {
        console.log('✅ FAVORITE BUTTON CLICKED:', btn, 'Product ID:', btn.getAttribute('data-product-id'));
        e.preventDefault();
        e.stopPropagation();
        
        const productId = btn.getAttribute('data-product-id');
        
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let cookie of cookies) {
                    cookie = cookie.trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const csrftoken = getCookie('csrftoken');
        
        fetch(`/toggle_favorite/${productId}/`, {
            method: 'POST',
            headers: { 
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin',
            body: JSON.stringify({})
        })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log('✅ Favorite toggled successfully:', data);
            btn.classList.toggle('favorited');
            const icon = btn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-solid');
                icon.classList.toggle('fa-regular');
            }
        })
        .catch(err => console.error('❌ Error toggling favorite:', err));
    }
}, true); // Capture phase

/* Lazy load all product images */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🖼️ Setting up lazy loading for images...');
    const images = document.querySelectorAll('img:not([loading="lazy"])');
    images.forEach(img => {
        if (!img.src.includes('placeholder')) {
            img.loading = 'lazy';
        }
    });
    
    // Also add lazy loading to picture elements
    const pictures = document.querySelectorAll('picture img');
    pictures.forEach(img => {
        img.loading = 'lazy';
    });
});