/**
* @param {HTMLTableElement}
* @param {number}
* @param {boolean}
*/

// console.log("Staff:", isStaff);
// Capture the current page URL to send as the "next" destination
const currentPath = encodeURIComponent(window.location.pathname + window.location.search);


//close notification
document.addEventListener('DOMContentLoaded', () => {
  (document.querySelectorAll('.notification .delete') || []).forEach(($delete) => {
    const $notification = $delete.parentNode;

    $delete.addEventListener('click', () => {
      $notification.parentNode.removeChild($notification);
    });
  });
});

// const modal = document.querySelector("#myModal");
// const closeModal = document.querySelector("#closeModal");

// Use querySelectorAll and a loop to attach to ALL edit buttons
document.querySelectorAll(".openModalBtn").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation(); // Prevents the row-click injection from firing too
        // modal.showModal();
    });
});

// closeModal.addEventListener("click", () => {
//     modal.close();
// });

function sortTableByColumn(table, column, asc = true) {
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    const sortedRows = rows.sort((a, b) => {
        const aColText = a.querySelector(`td:nth-child(${ column + 1})`).textContent.trim();
        const bColText = b.querySelector(`td:nth-child(${ column + 1})`).textContent.trim();
        
        return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);
    });

    console.log(sortedRows)

    // Remove all existing TRs from the table
    while (tBody.firstChild) {
        tBody.removeChild(tBody.firstChild);
    }

    // Re-add the newly sorted rows
    tBody.append(...sortedRows);
    
    // Remember how the column is currently sorted
    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);
}

document.querySelectorAll(".tableSortable th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAscending = headerCell.classList.contains("th-sort-asc");

        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
    });
});

$(document).ready(function() {
    var table = $('#table').DataTable({
        paging: true,
        pageLength: 50,
        lengthMenu: [[10, 100, 1000], [10, 100, 1000]],
        searching: true,
        ordering: true,
        order: [[0, 'asc']]
    });

    $('#table tbody').on('click', 'tr', function() {

        // Don’t trigger on the action row itself
        if ($(this).hasClass('action-row')) return;

        var $this = $(this);
        var pk = $this.data('pk'); // each row should have data-pk="{{ e.pk }}"
        var nextRow = $this.next('.action-row');

        // If the next row is already the action row and visible, toggle it off
        if (nextRow.length && nextRow.is(':visible')) {
            nextRow.remove();
            return;
        }

        // Otherwise, remove any other open action rows
        $('#table tbody tr.action-row').remove();

        // Create the button only if isStaff is true
        if (isStaff) {
            // Button for Admins
            editButton = `<a href="/edit/${pk}/?next=${currentPath}" class="button is-warning">Edit</a>`;
            
        } else {
            // Button for Regular Users
            editButton = `<a class="button is-warning openModalBtn" onclick="editNofication()">Edit</a>`;          
        }

        $('#table').on('click', '.openModalBtn', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevents the mobile row from closing
            
            const modal = document.querySelector("#myModal");
            // modal.showModal();
        });

        // Insert a new action row after this row
        var actionRow = `
            <tr class="action-row">
                <td colspan="${$this.children().length}">
                    <div class="action-box" style="text-align:center;">
                        ${editButton}
                        <a href="/delete/${pk}/" class="button is-danger">Delete</a>
                    </div>
                </td>
            </tr>
        `;
        $this.after(actionRow);
    });
});



//mobile row expansion
document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll(".clickable-row");

  rows.forEach((row, index) => {
    row.addEventListener("click", () => {
      // Only on mobile
      if (window.innerWidth <= 768) {
        const actionRow = row.nextElementSibling;
        if (actionRow && actionRow.classList.contains("action-row")) {
          actionRow.style.display = actionRow.style.display === "table-row" ? "none" : "table-row";
        }
      }
    });
  });
});


function editNofication() {
    const div = document.getElementById("editNotification");
    
    if (div.style.display === "none") {
        div.style.display = "block";
    } else {
        div.style.display = "none";
    }
}
// Frunction to close notification
function showBulmaNotification(message) {
    const container = document.getElementById('notification-container');

    // Create the notification element
    const notification = document.createElement('div');
    notification.className = 'notification is-danger';
    notification.innerHTML = `
        <button class="delete"></button>
        ${message}
    `;

    // Add logic to the "delete" button inside the notification
    notification.querySelector('.delete').addEventListener('click', () => {
        notification.remove();
    });

    // Add to the container
    container.appendChild(notification);

    // Optional: Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

