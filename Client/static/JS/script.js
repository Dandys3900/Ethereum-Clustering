/**
 * TODO:
 * session pwd timeout
 * tests
 * TLS
 */

function showRangeValue (exchLen, rangeElementValue=50) {
    document.getElementById("refreshLabel").innerText = `${rangeElementValue} %`;
    document.getElementById("exchLenLabel").innerText = Math.floor(exchLen * (rangeElementValue / 100));
}

function triggerAboutText () {
    const text = document.getElementById("aboutText");
    text.style.display = (text.style.display === "none") ? "block" : "none";
}

function showElement (elementId) {
    document.getElementById(elementId).style.display = "block";
}

function hideElement (elementId) {
    document.getElementById(elementId).style.display = "none";
}

async function submitRefreshRequest (event) {
    event.preventDefault();
    // Show spinner
    showElement("loadSpinner");

    // Create form and append extracted value to it
    const formData = new FormData();
    formData.append("minHeight", document.getElementById("minBlockHeight").value);
    formData.append("maxHeight", document.getElementById("maxBlockHeight").value);
    formData.append("scope"    , document.getElementById("refeshScope").value);
    // If user already loggedIn, this element doesn't exist
    if (document.getElementById("refreshPwd"))
        formData.append("pwd", CryptoJS.SHA512(document.getElementById("refreshPwd").value).toString());

    // Make sure maxBlock >= minBlock, else show error modal and skip sending to server
    if (formData.get("maxHeight") < formData.get("minHeight")) {
        showInfoModal("Invalid values: max. height < min. height");
        return;
    }

    const response = await fetch("/refreshDB", {
        method: "POST",
        body  : formData
    });

    // Hide spinner
    hideElement("loadSpinner");

    // Implicit success result
    var resultText = "Clustering process finished succesfully";
    if (!response.ok) {
        resultText = "Error happened during the clustering process";
        // Notify user about invalid password provided
        if (response.status === 401)
            resultText = "Invalid password provided, try again please...";
    }
    else {
        const { clientData, exchLen, addrsCount } = await response.json();
        // Update menu with new data (no need to refresh entire page)
        updateMenu(clientData, addrsCount, exchLen);
    }
    showInfoModal(resultText);
}

function updateMenu (clientData, addrsCount, exchLen) {
    // Update values non dependant on blockchain client status first
    document.getElementById("exchCountsItem").innerText  = addrsCount.get("exchanges", 0);
    document.getElementById("deposCountsItem").innerText = addrsCount.get("deposits", 0);
    document.getElementById("leafsCountsItem").innerText = addrsCount.get("leafs", 0);

    hideElement("clientUpItems");
    hideElement("clientDownItems");

    // If clientData is None, client is down, adapt menu to it
    if (clientData) {
        showElement("clientUpItems");
        document.getElementById("maxBlockItem").innerText = clientData.get("maxBlock", 0);
        document.getElementById("syncTimeItem").innerText = clientData.get("syncTime", "1970-01-01, 00:00");

        // Update refresh modal values as well
        showRangeValue(exchLen);
    }
    else {
        showElement("clientDownItems");
    }
    // Based on above, set click-ability to refresh DB button
    document.getElementById("refreshDBbutton").disabled = ((clientData) ? true : false);
}

async function showExchList (loggedIn=false, justUpdate=false) {
    // Get JSON list of exchanges from server
    const response = await fetch("/exchList", {
        method: "GET"
    });
    // Get JSON format for response
    const exchList = await response.json();

    document.getElementById("exchsListModalBody").innerHTML = "";
    // Just update table data if set
    if (justUpdate || window.exchTable) {
        window.exchTable.updateConfig({
            data: Object.keys(exchList).map(key => {
                // Key: Exch addr ; Value: Exch name
                return [key, exchList[key]];
            })
        }).forceRender();
    }
    else { // Create new table
        createExchListTable(loggedIn, exchList)
            .render(document.getElementById("exchsListModalBody"));
    }

    if (!justUpdate) // Show modal
        (new bootstrap.Modal(document.getElementById("exchsListModal"))).show();
}

function showEditModal (curAddr, curExchName) {
    // Prepare edit modal with current values
    document.getElementById("editModalAddr").value       = curAddr;
    document.getElementById("editModalAddr").placeholder = curAddr; // Keep original addr as placeholder for editExchAddr() call
    document.getElementById("editModalAddrName").value   = curExchName;

    // Show modal to user
    (new bootstrap.Modal(document.getElementById("editExchAddrModal"))).show();
}

async function addExchAddr () {
    // Send request to server
    const response = await fetch("/addAdr", {
        method: "POST",
        body  : JSON.stringify({
            newAddr  : document.getElementById("addModalAddr").value,
            newValue : document.getElementById("addModalAddrName").value
        })
    });

    // Reshow modal with new values
    showExchList(justUpdate=true);

    const result = await response.json();
    // Show result modal for user
    showInfoModal(
        `Adding exchange address result: ${result["result"]}`
    );
}

async function editExchAddr () {
    // Send request to server
    const response = await fetch("/editAdr", {
        method: "POST",
        body  : JSON.stringify({
            targetAddr : document.getElementById("editModalAddr").placeholder, // Stores original addr (see above in showEditModal())
            newAddr    : document.getElementById("editModalAddr").value,
            newValue   : document.getElementById("editModalAddrName").value
        })
    });

    // Reshow modal with new values
    showExchList(justUpdate=true);

    const result = await response.json();
    // Show result modal for user
    showInfoModal(
        `Edit exchange address result: ${result["result"]}`
    );
}

async function deleteExchAdr (curAddr) {
    // Send request to server
    const response = await fetch("/deleteAdr", {
        method: "POST",
        body  : JSON.stringify({
            targetAddr: curAddr
        })
    });

    // Reshow exchs modal with new values
    showExchList(justUpdate=true);

    const result = await response.json();
    // Show result modal for user
    showInfoModal(
        `Delete exchange address result: ${result["result"]}`
    );
}

async function doLoginIn () {
    const pwd = CryptoJS.SHA512(document.getElementById("loginPwd").value).toString();

    const response = await fetch("/logIn", {
        method: "POST",
        body  : JSON.stringify({
            pwd: pwd,
        })
    });

    const result = await response.json();
    // If login successful, refresh current page to show options for logged in
    if (result["result"] === "success")
        window.location.reload();
    else // Show modal about failed login
        showInfoModal(
            `LogIn failed: ${result["result"]}`
        );
}

function showInfoModal (text) {
    document.getElementById("infoText").innerText = text;
    (new bootstrap.Modal(document.getElementById("infoModal"))).show();
}

function exportJSON () {
    // When exporting, prefer selected nodes, default is all nodes
    downloadFile(
        "data.json",
        JSON.stringify(
            ((selectedNodes.size > 0) ? { nodes: Array.from(selectedNodes) } : { nodes: Object.keys(nodesParams) }), null, 2
        )
    );
}

function exportCSV () {
    header = ["nodes"]
    // When exporting, prefer selected nodes, default is all nodes
    downloadFile(
        "data.csv",
        (header.concat((selectedNodes.size > 0) ? Array.from(selectedNodes) : Object.keys(nodesParams))).join("\n")
    );
}

function downloadFile (filename, content) {
    /**
     * Function below, was taken from:
     * https://flexiple.com/javascript/download-flle-using-javascript
     * and scope of my changes was minimal or none.
     * Author: Siddharth Khuntwal
    */
    const blob = new Blob([content], { type: "text/plain" });
    const link = document.createElement("a");

    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

function copyToClipboard (value) {
    /**
     * Function below, was taken from:
     * https://stackoverflow.com/a/33928558/12801311
     * and scope of my changes was minimal or none.
     * Author: Greg Lowe (https://stackoverflow.com/users/1460491/greg-lowe)
    */
    const element = document.createElement("textarea");
    element.value = value;
    // Append and select
    document.body.appendChild(element);
    element.select();
    try { // Copy to clipboard
        document.execCommand("copy");
    }
    catch (ex) {
        console.warn("Copy to clipboard failed: ", ex);
    }
    // Remove afterwards
    document.body.removeChild(element);
}

function copyDonateText () {
    copyToClipboard("0x81E11145Fc60Da6ebD43eee7c19e18Ce9e21Bfd5");
    // Append it to existing element
    const element = document.getElementById("donateText");
    // Append success icon to text
    element.innerHTML = `✅ ${element.innerHTML}`;

    // Remove info text after 1s
    setTimeout(() => {
        // Set substring effectively removing added green tick icon
        element.innerHTML = String(element.innerHTML).substring(1);
    }, 1000);
}

function triggerLeftRow (whichBtn) {
    // Change visibility of outter trigger button
    const btn = document.getElementById("outterBtn");
    btn.style.display = (whichBtn === "innerBtn") ? "block" : "none";

    // Change visibility of left column
    const col = document.getElementById("results");
    col.style.display = (col.style.display === "none") ? "block" : "none";

    // When results table is shown and user entered address is selected, ensure being highlighted
    // This applies to initial page load where can't interact with table directly as being hidden
    if (col.style.display === "block" && selectedNodes.has(userAddr))
        setHighlightResultsTableItem(userAddr);

    // Ensure resize of chart
    addrChart.resize();
}

function setHighlightResultsTableItem (addr, highlight=true) {
    // Find it and set proper highlight class
    document.getElementById("dataTable").querySelectorAll(".gridjs-tr").forEach(row => {
        const value = row.innerText.trim();

        if (value.includes(addr)) {
            if (highlight) {
                row.classList.add("selected-row");
                selectedNodes.add(value);
            }
            else {
                row.classList.remove("selected-row");
                selectedNodes.delete(value);
            }
        }
    });

    // Update shown cluster count if any selected addresses
    if (selectedNodes.size > 0) {
        document.getElementById("addrCount").innerHTML = `&nbsp;Selected addresses in cluster: ${selectedNodes.size}`;
        document.getElementById("usedEther").innerHTML = `&nbsp;Transferred Ether by selected: ${Number(
            [...selectedNodes]
                .reduce((sum, key) => sum + nodesParams[key].amount, 0.0)
        ).toFixed(3)}`;
    }
    else { // All nodes count
        document.getElementById("addrCount").innerHTML = `&nbsp;Addresses in cluster: ${Object.keys(nodesParams).length}`;
        document.getElementById("usedEther").innerHTML = `&nbsp;Transferred Ether by cluster:${Number(
            Object.values(nodesParams)
                /**
                 * When showing overview of used Ether of the cluster, filter amount with source in deposit.
                 * Deposit sends only to exchange (other txs are ignored in DB), using it will only double
                 * total send amount of Ether and would confuse the user.
                 */
                .filter(item => item.type !== "deposit")
                .reduce((sum, item) => sum + item.amount, 0.0)
        ).toFixed(3)}`;
    }

    // Update graph nodes, add focus to selected address
    graph.nodes = graph.nodes.map(node => {
        // Determine node correct type/category
        const type = ((selectedNodes.has(node.id)) ? "selected" : node.props.type);

        return {
            ...node,
            symbolSize: nodeStyles[type].size,
            category  : type
        };
    });

    // Propagate change to graph
    addrChart.setOption({
        series: [{
            data: graph.nodes
        }]
    });
}

function toggleProceedBtn (pwdValue) {
    document.getElementById("proceedBtn").disabled = (pwdValue === "");
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

function createResultsTable () {
    return (window.resTable = new gridjs.Grid({
        columns: [
            "Entity"
        ],
        data: Object.keys(nodesParams).map(key => [
            gridjs.html(
                `<span style="display: inline-block; width: 10px; height: 10px; background-color: ${nodesParams[key].style.color}; border-radius: 2px;"></span>
                ${key}`
            )
        ]),
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

function processGraphData (graphData) {
    return {
        nodes: graphData.nodes.map(node => {
            // Store node params
            nodesParams[node.id] = {
                amount: 0.0, // Initial value
                type  : node.props.type,
                style : nodeStyles[node.props.type]
            };

            return {
                ...node,
                nodename  : node.id,
                exchname  : node.props.name,
                symbolSize: nodeStyles[node.props.type].size,
                category  : node.props.type
            };
        }),
        links: graphData.edges.map(edge => {
            // Accumulate address Ether amount
            nodesParams[edge.src].amount += parseFloat(edge.props.amount);

            return {
                source: edge.src,
                target: edge.dst,
                amount: edge.props.amount,
                txs   : edge.props.txs
            };
        }),
        categories: Object.keys(nodeStyles).map(function (category) {
            return {
                name: category
            };
        })
    };
}
