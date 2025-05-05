//// Tab switching functionality
//document.addEventListener("DOMContentLoaded", () => {
//  // Get all nav items and tab contents
//  const navItems = document.querySelectorAll(".nav-item")
//  const tabContents = document.querySelectorAll(".tab-content")
//
//  // Add click event to each nav item
//  navItems.forEach((navItem, index) => {
//    navItem.addEventListener("click", function () {
//      // Remove active class from all nav items
//      navItems.forEach((item) => {
//        item.classList.remove("active")
//      })
//
//      // Add active class to clicked nav item
//      this.classList.add("active")
//
//      // Hide all tab contents
//      tabContents.forEach((content) => {
//        content.classList.remove("active")
//      })
//
//      // Show corresponding tab content (if it exists)
//      if (tabContents[index]) {
//        tabContents[index].classList.add("active")
//      }
//
//      // Scroll to top of content area
//      document.querySelector(".main-content").scrollTo(0, 0)
//    })
//  })
//
//  // Mobile menu toggle
//  const mobileToggle = document.querySelector(".mobile-menu-toggle button")
//  const sidebar = document.querySelector(".sidebar")
//
//  if (mobileToggle && sidebar) {
//    mobileToggle.addEventListener("click", () => {
//      sidebar.classList.toggle("active")
//    })
//  }
//})
//
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');

            // Hide all tab contents
            tabContents.forEach(content => {
                content.classList.remove('active');
            });

            // Deactivate all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
            });

            // Activate selected tab
            document.getElementById(tabId).classList.add('active');
            this.classList.add('active');

            // Update URL without reload
            const url = new URL(window.location);
            url.searchParams.set('tab', tabId);
            window.history.pushState({}, '', url);
        });
    });

    // Mobile menu toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }

    // Initialize with correct tab from URL
    const urlParams = new URLSearchParams(window.location.search);
    const activeTab = urlParams.get('tab');

    if (activeTab) {
        const tabButton = document.querySelector(`.nav-item[data-tab="${activeTab}"]`);
        const tabContent = document.getElementById(activeTab);

        if (tabButton && tabContent) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));

            tabContent.classList.add('active');
            tabButton.classList.add('active');
        }
    }

    // Image preview for avatar upload
    const imageInput = document.querySelector('input[type="file"]');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.querySelector('.avatar-preview img').src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});