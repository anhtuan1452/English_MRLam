// Tab switching functionality
document.addEventListener("DOMContentLoaded", () => {
  // Get all nav items and tab contents
  const navItems = document.querySelectorAll(".nav-item")
  const tabContents = document.querySelectorAll(".tab-content")

  // Add click event to each nav item
  navItems.forEach((navItem, index) => {
    navItem.addEventListener("click", function () {
      // Remove active class from all nav items
      navItems.forEach((item) => {
        item.classList.remove("active")
      })

      // Add active class to clicked nav item
      this.classList.add("active")

      // Hide all tab contents
      tabContents.forEach((content) => {
        content.classList.remove("active")
      })

      // Show corresponding tab content (if it exists)
      if (tabContents[index]) {
        tabContents[index].classList.add("active")
      }

      // Scroll to top of content area
      document.querySelector(".main-content").scrollTo(0, 0)
    })
  })

  // Mobile menu toggle
  const mobileToggle = document.querySelector(".mobile-menu-toggle button")
  const sidebar = document.querySelector(".sidebar")

  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener("click", () => {
      sidebar.classList.toggle("active")
    })
  }
})

