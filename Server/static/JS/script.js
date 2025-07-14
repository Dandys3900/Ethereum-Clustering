function showRangeValue(rangeElement, exchLen) {
    document.getElementById("refreshLabel").innerText = rangeElement.value + " %";
    document.getElementById("exchLenLabel").innerText = Math.floor(exchLen * (rangeElement.value / 100));
}

function triggerMenu() {
    const form = document.getElementById("refreshForm");
    form.style.display = (form.style.display === "none") ? "block" : "none";
}

function triggerAboutText() {
    const text = document.getElementById("aboutText");
    text.style.display = (text.style.display === "none") ? "block" : "none";
}

function showElement(elementId) {
    document.getElementById(elementId).style.display = "block";
}

function hideElement(elementId) {
    document.getElementById(elementId).style.display = "none";
}

async function submitRefreshRequest(event) {
    event.preventDefault();
    // Show spinner
    showElement("loadSpinner");

    // Create form and append extracted value to it
    const formData = new FormData();
    formData.append("minHeight", document.getElementById("minBlockHeight").value);
    formData.append("maxHeight", document.getElementById("maxBlockHeight").value);
    formData.append("scope", document.getElementById("refeshScope").value);
    formData.append("pwd",   CryptoJS.SHA512(document.getElementById("refreshPwd").value).toString());

    const response = await fetch("/refreshDB", {
        method: "POST",
        body  : formData
    });

    // Hide spinner
    hideElement("loadSpinner");

    if (!response.ok) {
        let defaultError = "Error happened during the clustering process";
        // Notify user about invalid password provided
        if (response.status === 401)
            defaultError = "Invalid password provided, try again please...";
        // Set alert text
        document.getElementById("alertText").innerText = defaultError;
        (new bootstrap.Modal(document.getElementById("errorText"))).show();
    }
    else {
        const { syncDate, addrsCount, exchLen } = await response.json();
        // Update menu with new data (no need to refresh entire page)
        createMenu(document.getElementById("refreshForm"), syncDate, addrsCount, exchLen);
    }
}

function exportJSON() {
    // When exporting, prefer selected nodes, default is all nodes
    downloadFile(
        "data.json",
        JSON.stringify(
            ((selectedNodes.size > 0) ? { nodes: Array.from(selectedNodes) } : { nodes: Object.keys(nodesParams) }), null, 2
        )
    );
}

function exportCSV() {
    header = ["nodes"]
    // When exporting, prefer selected nodes, default is all nodes
    downloadFile(
        "data.csv",
        (header.concat((selectedNodes.size > 0) ? Array.from(selectedNodes) : Object.keys(nodesParams))).join("\n")
    );
}

function downloadFile(filename, content) {
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

function copyToClipboard(value) {
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

function copyDonateText() {
    copyToClipboard("0x81E11145Fc60Da6ebD43eee7c19e18Ce9e21Bfd5");
    // Append it to existing element
    const element = document.getElementById("donateText");
    // Append success icon to text
    element.innerHTML = "✅" + element.innerHTML;

    // Remove info text after 1s
    setTimeout(() => {
        // Set substring effectively removing added green tick icon
        element.innerHTML = String(element.innerHTML).substring(1);
    }, 1000);
}

function triggerLeftRow(whichBtn) {
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

function setHighlightResultsTableItem(addr, highlight=true) {
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

function toggleProceedBtn(pwdValue) {
    document.getElementById("proceedBtn").disabled = (pwdValue === "");
}

function createTxTable() {
    return new gridjs.Grid({
        columns: [
            {
                name : "Transaction",
                attributes: { style: "width: 50%;" }
            },
            "Time",
            "Amount",
            {
                name     : "Show on EtherScan🕵️",
                formatter: (_, row) => gridjs.html(`<b><a href='https://etherscan.io/tx/${row.cells[0].data}' target='_blank'>Link</a></b>`)
            }
        ],
        data: [],
        pagination: {
            limit: 20
        },
        resizable: true,
        search   : true
    });
}

function createResultsTable() {
    return new gridjs.Grid({
        columns: ["Entity"],
        data: Object.keys(nodesParams).map(value => [
            gridjs.html(`
                <span style="display: inline-block; width: 10px; height: 10px; background-color: ${nodesParams[value].style.color}; border-radius: 2px;"></span>
                ${value}
            `)
        ]),
        pagination: {
            limit: 20
        },
        resizable: true,
        search   : true
    })
}

function processGraphData() {
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
