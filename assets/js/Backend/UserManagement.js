import { multiselect_options } from "../Constants";

export default class UserManagement {
    constructor() {
        $('#subsites').multiselect(multiselect_options);
        $('#capabilities').multiselect(multiselect_options);
    }
}
