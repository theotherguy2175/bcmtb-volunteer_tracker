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
    // Find the index of the column with the 'default-sort' class
    var sortIndex = $('#table thead th.default-sort').index();
    console.log("Default sort index:", sortIndex);
    // 1. Initialize the table with Export Buttons
    var table = $('#table').DataTable({
    // l = Length (show X lines)
    // B = Buttons (Export CSV)
    // f = Filter (Search bar)
    // r = pRocessing
    // t = Table
    // i = Info (Showing 1 of 50...)
    // p = Pagination
    dom: '<"columns is-mobile is-vcentered"<"column"l><"column has-text-centered"B><"column"f>>rtip',
    buttons: [
        {
            extend: 'csvHtml5',
            text: 'Export CSV',
            className: 'button is-info is-small',
            exportOptions: {
                rows: function (idx, data, node) {
                    return !$(node).hasClass('action-row');
                }
            }
        }
    ],

    order: [[sortIndex, 'desc']],  // Default sort by first column descending
    columnDefs: [
            { "type": "num", "targets": sortIndex } // Tells DataTables to treat data-order as a number
        ],
    paging: true,
    pageLength: 50,
    lengthMenu: [[10, 100, 1000], [10, 100, 1000]],
    });

    // 2. Handle the Row Clicks for the Expandable Edit/Delete buttons
    $('#table tbody').on('click', 'tr', function() {
        if ($(this).hasClass('action-row')) return;

        var $this = $(this);
        var pk = $this.data('pk');
        var nextRow = $this.next('.action-row');

        if (nextRow.length && nextRow.is(':visible')) {
            nextRow.remove();
            return;
        }

        $('#table tbody tr.action-row').remove();

        // Define currentPath for the "next" redirect
        const currentPath = encodeURIComponent(window.location.pathname + window.location.search);

        let editButton = '';

        if (isStaff) {
            // Button for Admins - uses the 'next' parameter we built
            editButton = `<a href="/edit/${pk}/?next=${currentPath}" class="button is-warning">Edit</a>`;
        } else {
            // Button for Regular Users - triggers your notification/modal
            editButton = `<a class="button is-warning openModalBtn">Edit</a>`;          
        }

        var actionRow = `
            <tr class="action-row">
                <td colspan="${$this.children().length}">
                    <div class="action-box" style="text-align:center; padding: 10px; background: #f5f5f5;">
                        ${editButton}
                        <a href="/delete/${pk}/?next=${currentPath}" class="button is-danger">Delete</a>
                    </div>
                </td>
            </tr>
        `;
        $this.after(actionRow);
    });

    // 3. Delegation for the openModalBtn (placed outside the row click)
    $('#table').on('click', '.openModalBtn', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Trigger your Bulma notification or Modal here
        if (typeof editNofication === "function") {
            editNofication(); 
        }
        
        // If you want the browser <dialog>:
        // document.querySelector("#myModal").showModal();
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

