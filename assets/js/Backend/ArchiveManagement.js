
export default class ArchiveManagement {
    constructor() {
        $('#archive-categories .expand').click((evt) => {
            let arrow = $(evt.target);
            if (arrow.parent().data('status') === 'closed') {
                arrow.removeClass('fa-arrow-circle-o-right').addClass('fa-arrow-circle-o-down');
                arrow.parent().data('status', 'open');
                arrow.parent().next().slideDown();
            }
            else {
                arrow.removeClass('fa-arrow-circle-o-down').addClass('fa-arrow-circle-o-right');
                arrow.parent().data('status', 'closed');
                arrow.parent().next().slideUp();
            }
        });
    }
}