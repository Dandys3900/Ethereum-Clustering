function createModal(style="", id="", head="", body="", bodyId="", footer="") {
    const location = document.currentScript;
    if (!location)
        return;

    location.insertAdjacentHTML('beforebegin', `
        <div class="modal fade" role="dialog" tabindex="-1" id="${id || ''}" style="${style || ''}">
            <div class="modal-dialog" style="max-width: 70%; margin: auto;">
                <div class="modal-content">
                    ${head             ? `<div class="modal-header">${head} <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>` : ''}
                    ${(body || bodyId) ? `<div class="modal-body" id="${bodyId || ''}">${body}</div>`                                                        : ''}
                    ${footer           ? `<div class="modal-footer">${footer}</div>`                                                                         : ''}
                </div>
            </div>
        </div>
    `);
}
