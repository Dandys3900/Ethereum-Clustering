function createModal ({style="", id="", header="", body="", bodyId="", footer=""}) {
    const modalHTML =
        `<div class="modal fade" role="dialog" tabindex="-1" ${id ? `id="${id}"` : ''}>
            <div class="modal-dialog" ${style ? `style="${style}"` : ''}>
                <div class="modal-content">
                    <div class="modal-header">${header} <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                    ${(body || bodyId) ? `<div class="modal-body" id="${bodyId || ''}">${body}</div>` : ''}
                    ${footer           ? `<div class="modal-footer">${footer}</div>`                  : ''}
                </div>
            </div>
        </div>`;

    // Append to body's end
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function createResultsTable () {
    return (window.resTable = new gridjs.Grid({
        columns: [
            { name: "Hidden-Values", hidden: true }, // Helper column to get addrs directly
            "Entity"
        ],
        data: Object.keys(nodesParams).map(key => {
            return [
                key,
                gridjs.html(
                    `<span style="display: inline-block; width: 10px; height: 10px; background-color: ${nodesParams[key].style.color}; border-radius: 2px;"></span>
                    ${key}`
                )
            ];
        }),
        pagination: {
            limit: 20
        },
        search: true
    }));
}

function createExchListTable (loggedIn, exchListData) {
    return (window.exchTable = new gridjs.Grid({
        columns: [
            {
                name : "Exchange address",
                attributes: {
                    style: "width: 50%;"
                }
            },
            "Exchange name",
            ...(loggedIn ? [{
                    name     : "Actions",
                    formatter: (_, row) => {
                        return gridjs.html(
                            `<div style="display: flex; gap: 10px; cursor: pointer;">
                                <b><a href='https://etherscan.io/address/${row.cells[0].data.toLowerCase()}' target='_blank'>🔍</a></b>
                                <b><a onclick='showEditModal("${row.cells[0].data}", "${row.cells[1].data}")'>🖉</a></b>
                                <b><a onclick='deleteExchAdr("${row.cells[0].data}")'>🗑️</a></b>
                            </div>`
                        );
                    }
                }] : [])
        ],
        data: Object.keys(exchListData).map(key => {
            // Key: Exch addr ; Value: Exch name
            return [key, exchListData[key]];
        }),
        pagination: {
            limit: 20
        },
        resizable: true,
        search   : true
    }));
}

function createTxTable () {
    return (window.txTable = new gridjs.Grid({
        columns: [
            {
                name : "Transaction",
                attributes: {
                    style: "width: 50%;"
                }
            },
            "Time",
            "Amount",
            {
                name     : "Actions",
                formatter: (_, row) => {
                    return gridjs.html(
                        `<b><a href='https://etherscan.io/tx/${row.cells[0].data}' target='_blank' label='Show on EtherScan'>🕵️</a></b>`
                    );
                }
            }
        ],
        data: [],
        pagination: {
            limit: 20
        },
        resizable: true,
        search   : true
    }));
}
