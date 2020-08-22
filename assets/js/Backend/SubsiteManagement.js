import { multiselect_options } from "../Constants";

export default class SubsiteManagement {
    constructor() {
        $('#categories').multiselect(multiselect_options)
    }
}
