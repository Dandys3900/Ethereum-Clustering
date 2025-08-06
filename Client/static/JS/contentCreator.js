function createModal({style="", id="", head="", body="", bodyId="", footer=""}) {
    const modalHTML =
        `<div class="modal fade" role="dialog" tabindex="-1" ${id ? `id="${id}"` : ''} ${style ? `style="${style}"` : ''}>
            <div class="modal-dialog" style="margin: auto;">
                <div class="modal-content">
                    <div class="modal-header">${head} <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
                    ${(body || bodyId) ? `<div class="modal-body" id="${bodyId || ''}">${body}</div>`                                                        : ''}
                    ${footer           ? `<div class="modal-footer">${footer}</div>`                                                                         : ''}
                </div>
            </div>
        </div>`;

    // Append to body's end
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}
