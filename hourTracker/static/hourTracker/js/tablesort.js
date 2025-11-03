/**
* @param {HTMLTableElement}
* @param {number}
* @param {boolean}
*/

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

        // Insert a new action row after this row
        var actionRow = `
            <tr class="action-row">
                <td colspan="${$this.children().length}">
                    <div class="action-box" style="text-align:center;">
                        <a href="/edit/${pk}/" class="button is-warning">Edit</a>
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