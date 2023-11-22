document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const taskTable = document.getElementById('tasktable');
    const tableRows = taskTable.getElementsByTagName('tr');

    searchInput.addEventListener('input', function () {
        const searchTerm = searchInput.value.toLowerCase();

        for (let i = 0; i < tableRows.length; i++) {
            const cells = tableRows[i].getElementsByTagName('td');
            let found = false;

            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].innerText.toLowerCase();

                if (cellText.includes(searchTerm)) {
                    found = true;
                    break;
                }
            }

            tableRows[i].style.display = found ? '' : 'none';
        }
    });
});