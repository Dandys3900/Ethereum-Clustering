function createModal({style="", id="", header="", body="", bodyId="", footer=""}) {
    const modalHTML =
        `<div class="modal fade" role="dialog" tabindex="-1" ${id ? `id="${id}"` : ''}>
            <div class="modal-dialog" ${style ? `style="${style}"` : ''}>
                <div class="modal-content">
                    <div class="modal-header">${header} <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                    ${(body || bodyId) ? `<div class="modal-body" id="${bodyId || ''}">${body}</div>`                                                        : ''}
                    ${footer           ? `<div class="modal-footer">${footer}</div>`                                                                         : ''}
                </div>
            </div>
        </div>`;

    // Append to body's end
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}
