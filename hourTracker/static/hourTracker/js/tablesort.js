/**
* @param {HTMLTableElement}
* @param {number}
* @param {boolean}
*/

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

// Use querySelectorAll and a loop to attach to ALL edit buttons
document.querySelectorAll(".openModalBtn").forEach(btn => {
    btn.addEventListener("click", (e) => {
        e.stopPropagation(); // Prevents the row-click injection from firing too
        // modal.showModal();
    });
});

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
    
    // 1. Initialize the table
    var table = $('#table').DataTable({
        // We simplified 'dom'. 
        // 'lBfrtip' puts everything in a plain list so we can grab them easily.
        dom: 'lBfrtip',
        
        language: {
            search: "", // Removes the "Search:" label
            searchPlaceholder: "Search...", // Text inside the box
            lengthMenu: "_MENU_" // Removes "entries" text to keep it tight
        },
        // This runs as soon as the table is finished building
        initComplete: function() {
            // Add Bulma 'input' class to the search box
            $('.dataTables_filter input').addClass('input');
            
            // Add Bulma 'select' wrapper and class to the length dropdown
            $('.dataTables_length select').addClass('select dropdown');
            $('.dataTables_length').addClass('select');
            $('.dataTables_length select').val('100').change();
        },
        
        buttons: [
            {
                extend: 'csvHtml5',
                text: '<span class="button is-info">Export CSV</span>',
                className: 'button is-info is-small is-rounded', 
                    init: function(api, node, config) {
                        // This targets the <button> tag you highlighted in your screenshot
                        $(node).attr('style', 'border: none !important; background: transparent !important; padding: 0 !important; box-shadow: none !important; outline: none !important;');
                    },
                exportOptions: {
                    rows: function (idx, data, node) {
                        return !$(node).hasClass('action-row');
                    }
                }
            }
        ],
        order: [[sortIndex, 'desc']],
        columnDefs: [
            { "type": "num", "targets": sortIndex }
        ],
        paging: true,
        pageLength: 100,
        lengthMenu: [
        [10, 100, 1000], //actual values for logic
        [10, 100, 1000] //displayed values on page
    ],
    });

    var $controls = $('<div class="columns is-mobile is-vcentered"></div>');
    // 1. Left: Narrow column (only as wide as the dropdown)
    var $leftCol = $('<div class="column is-narrow"></div>').append($('.dataTables_length'));
    $controls.append($leftCol);
    // 2. Center: Narrow column (only as wide as the button)
    var $centerCol = $('<div class="column is-narrow" style="border:none"></div>').append($('.dt-buttons'));
    $controls.append($centerCol);
    // 3. Right: Flex column (takes up 100% of the REMAINING space)
    var $rightCol = $('<div class="column"></div>').append($('.dataTables_filter'));
    $controls.append($rightCol);

    $('#datatable-controls').empty().append($controls);


// 2. Handle the Row Clicks for the Expandable Edit/Delete buttons
    $('#table tbody').on('click', 'tr', function() {
        if (window.innerWidth > 768) return; 
        if ($(this).hasClass('action-row')) return;
        
        var $this = $(this);
        var pk = $this.data('pk');
        
        // Ensure the main row has a specific ID so we can target it for deletion
        if (!$this.attr('id')) {
            $this.attr('id', 'row-' + pk);
        }

        var nextRow = $this.next('.action-row');

        if (nextRow.length && nextRow.is(':visible')) {
            nextRow.remove();
            return;
        }

        $('#table tbody tr.action-row').remove();

        const currentPath = encodeURIComponent(window.location.pathname + window.location.search);
        let editButton = '';

        if (isStaff) {
            editButton = `<a href="/edit/${pk}/?next=${currentPath}" class="button is-warning">Edit</a>`;
        } else {
            editButton = `<a class="button is-warning openModalBtn">Edit</a>`;          
        }

        // ... inside your $('#table tbody').on('click', 'tr', function() ...

        // 1. Ensure the main row has the ID so HTMX can find it
        // $this.attr('id', 'row-' + pk); 

        // 2. Updated Action Row
        var actionRow = `
            <tr class="action-row" id="actions-${pk}">
                <td colspan="${$this.children().length}">
                    <div class="action-box" style="text-align:center; padding: 10px; background: #363636; border-radius: 4px;">
                        ${editButton}
                        <button 
                            hx-post="/delete/${pk}/" 
                            hx-target="#row-${pk}" 
                            hx-swap="outerHTML swap:0.5s" 
                            hx-confirm="Are you sure?"
                            hx-on::after-request="if(event.detail.successful) $('#actions-${pk}').remove();"
                            class="button is-danger">
                            Delete
                        </button>
                    </div>
                </td>
            </tr>
        `;

    

        $this.after(actionRow);

        // Crucial: Tell HTMX to initialize the button we just injected
        htmx.process(document.getElementById("actions-" + pk));
    });


    // 3. Delegation for the openModalBtn
    $('#table').on('click', '.openModalBtn', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (typeof editNofication === "function") {
            editNofication(); 
        }
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

