import moment from 'moment';
import 'moment-timezone';

export const removeZ = (value) => {
    if (!value)
        return value;
    if (value.slice(-1) === 'Z')
        return value.slice(0, -1);
    return value;
};

export const formatDatetime = (value, empty, utc) => {
    if (!value) {
        if (empty)
            return empty;
        return '';
    }
    return moment.utc(removeZ(value)).tz('Europe/Berlin').format('DD.MM., HH:mm:ss');
};
