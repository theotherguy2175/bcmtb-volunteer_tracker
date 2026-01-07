/*=============== SHOW MENU ===============*/
const navMenu = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose = document.getElementById('nav-close')

/* Menu show */
if(navToggle){
   navToggle.addEventListener('click', () =>{
      navMenu.classList.add('show-menu')
   })
}

/* Menu hidden */
if(navClose){
   navClose.addEventListener('click', () =>{
      navMenu.classList.remove('show-menu')
   })
}

/*=============== REMOVE MENU MOBILE ===============*/
const navLink = document.querySelectorAll('.nav__link')

const linkAction = () =>{
   const navMenu = document.getElementById('nav-menu')
   // When we click on each nav__link, we remove the show-menu class
   navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))

/*=============== SHOW DROPDOWN ===============*/
const showDropdown = (dropdownId) =>{
   const dropdown = document.getElementById(dropdownId)

   dropdown.addEventListener('click', ()=>{
      /* Show dropdown */
      dropdown.classList.toggle('show-dropdown')
   })
}
showDropdown('dropdown')

/*=============== LOGOUT FUNCTIONALITY ===============*/
document.addEventListener("DOMContentLoaded", function() {
    const logoutLink = document.getElementById("logout-link");
    if (logoutLink) {
        logoutLink.addEventListener("click", function(e) {
            e.preventDefault();
            document.getElementById("logout-form").submit();
        });
    }
});

function formatMobileButton() {
    const $btn = $('#mobile-button');
    const $btnText = $btn.find('.btn-text');
    
    if ($(window).width() <= 768) {
        // 1. Remove Bulma classes
        $btn.removeClass('button is-primary');
        
        // 2. Hide the text
        $btnText.hide();
        
        // 3. Apply floating styles directly to the element
        $btn.css({
            'position': 'fixed',
            'bottom': '25px',
            'right': '25px',
            'background-color': '#00d1b2', // Bulma Primary Green
            'color': '#fff',
            'width': '60px',
            'height': '60px',
            'border-radius': '50%',
            'display': 'flex',
            'align-items': 'center',
            'justify-content': 'center',
            'z-index': '9999',
            'box-shadow': '0 4px 10px rgba(0,0,0,0.3)',
            'border': 'none'
        });
    } else {
        // Desktop: Restore Bulma classes and reset inline styles
        $btn.addClass('button is-primary');
        $btnText.show();
        $btn.removeAttr('style');
    }
}

// Initialize on load and resize
$(window).on('load resize', formatMobileButton);