/*!
 * Pikaday
 *
 * Copyright © 2014 David Bushell | BSD & MIT license | https://github.com/dbushell/Pikaday
 * Pikatime (c) 2017 Helly as derivation for Domotion
 */

(function (root, factory)
{
    'use strict';

    if (typeof exports === 'object') {
        // CommonJS module
        module.exports = factory();
    } else if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(function (req)
        {
            return factory();
        });
    } else {
        root.Pikatime = factory();
    }
}(this, function ()
{
    'use strict';

    /**
     * feature detection and helper functions
     */
    var hasEventListeners = !!window.addEventListener,

    document = window.document,

    sto = window.setTimeout,

    addEvent = function(el, e, callback, capture)
    {
        if (hasEventListeners) {
            el.addEventListener(e, callback, !!capture);
        } else {
            el.attachEvent('on' + e, callback);
        }
    },

    removeEvent = function(el, e, callback, capture)
    {
        if (hasEventListeners) {
            el.removeEventListener(e, callback, !!capture);
        } else {
            el.detachEvent('on' + e, callback);
        }
    },

    fireEvent = function(el, eventName, data)
    {
        var ev;

        if (document.createEvent) {
            ev = document.createEvent('HTMLEvents');
            ev.initEvent(eventName, true, false);
            ev = extend(ev, data);
            el.dispatchEvent(ev);
        } else if (document.createEventObject) {
            ev = document.createEventObject();
            ev = extend(ev, data);
            el.fireEvent('on' + eventName, ev);
        }
    },

    trim = function(str)
    {
        return str.trim ? str.trim() : str.replace(/^\s+|\s+$/g,'');
    },

    hasClass = function(el, cn)
    {
        return (' ' + el.className + ' ').indexOf(' ' + cn + ' ') !== -1;
    },

    addClass = function(el, cn)
    {
        if (!hasClass(el, cn)) {
            el.className = (el.className === '') ? cn : el.className + ' ' + cn;
        }
    },

    removeClass = function(el, cn)
    {
        el.className = trim((' ' + el.className + ' ').replace(' ' + cn + ' ', ' '));
    },

    isArray = function(obj)
    {
        return (/Array/).test(Object.prototype.toString.call(obj));
    },

    isDate = function(obj)
    {
        return (/Date/).test(Object.prototype.toString.call(obj)) && !isNaN(obj.getTime());
    },

    extend = function(to, from, overwrite)
    {
        var prop, hasProp;
        for (prop in from) {
            hasProp = to[prop] !== undefined;
            if (hasProp && typeof from[prop] === 'object' && from[prop] !== null && from[prop].nodeName === undefined) {
                if (isDate(from[prop])) {
                    if (overwrite) {
                        to[prop] = new Date(from[prop].getTime());
                    }
                }
                else if (isArray(from[prop])) {
                    if (overwrite) {
                        to[prop] = from[prop].slice(0);
                    }
                } else {
                    to[prop] = extend({}, from[prop], overwrite);
                }
            } else if (overwrite || !hasProp) {
                to[prop] = from[prop];
            }
        }
        return to;
    },

    /**
     * defaults and localisation
     */
    defaults = {

        // bind the picker to a form field
        field: null,

        // automatically show/hide the picker on `field` focus (default `true` if `field` is set)
        bound: undefined,

        // position of the timepicker, relative to the field (default to bottom & left)
        // ('bottom' & 'left' keywords are not used, 'top' & 'right' are modifier on the bottom/left position)
        position: 'bottom left',

        // automatically fit in the viewport even if it means repositioning from the position option
        reposition: true,

        // the default output format for `.toString()` and `field` value
        format: '', //YYYY-MM-DD',

        // the initial time to view when first opened
        defaultTime: null,

        // make the `defaultTime` the initial selected value
        setdefaultTime: false,

        // the minimum/earliest time that can be selected
        minTime: null,
        // the maximum/latest time that can be selected
        maxTime: null,

        // used internally (don't config outside)
        minHour: 0,
        maxHour: 23,
        minMinutes: 0,
        maxMinutes: 59,
        minSeconds: 0,
        maxSeconds: 59,

        startRange: null,
        endRange: null,

        // Specify a DOM element to render the calendar in
        container: undefined,

        // Theme Classname
        theme: null,

        // callback function
        onSelect: null,
        onOpen: null,
        onClose: null,
        onDraw: null
    },

    /**
     * templating functions to abstract HTML rendering
     */
    renderIncrRow = function(instance)
    {
        var html = '<tr>';

        // Hours
        html += '<td><button class="pikt-incr pikt-incr-hours" type="button"></button></td>';

        // Minutes
        html += '<td></td><td><button class="pikt-incr pikt-incr-minutes" type="button"></button></td>';

        // Seconds
        if (instance._time.hasseconds) {
            html += '<td></td><td><button class="pikt-incr pikt-incr-seconds" type="button"></button></td>';
        }

        // AM/ PM
        if (instance._time.clock12h) {
            html += '<td></td><td><button class="pikt-incr pikt-incr-pm" type="button"></button></td>';
        }        

        html += '</tr>';

        return html;
    },

    renderDecrRow = function(instance)
    {
        var html = '<tr>';

        // Hours
        html += '<td><button class="pikt-decr pikt-decr-hours" type="button"></button></td>';

        // Minutes
        html += '<td></td><td><button class="pikt-decr pikt-decr-minutes" type="button"></button></td>';

        // Seconds
        if (instance._time.hasseconds) {
            html += '<td></td><td><button class="pikt-decr pikt-decr-seconds" type="button"></button></td>';
        }

        // AM/ PM
        if (instance._time.clock12h) {
            html += '<td></td><td><button class="pikt-decr pikt-decr-pm" type="button"></button></td>';
        }        

        html += '</tr>';

        return html;
    },

    renderTimeRow = function(instance)
    {
        var i, arr;
        var html = '<tr>';

        // Hours
        var h = (instance._time.hours < 10 ? '0' : '' ) + instance._time.hours;
        if (instance._time.clock12h) {
            for (arr = [], i = 1; i <= 12; i++) {
                arr.push('<option value="' + i + '"' +
                    (i === instance._time.hours ? ' selected="selected"': '') + '>' +
                    (i < 10 ? '0' : '' ) + i + '</option>');
            }
        } else {
            for (arr = [], i = 0; i < 24; i++) {
                arr.push('<option value="' + i + '"' +
                    (i === instance._time.hours ? ' selected="selected"': '') + '>' +
                    (i < 10 ? '0' : '' ) + i + '</option>');
            }
        }
        html += '<td><div class="pikt-label">' + h + '<select class="pikt-select pikt-select-hours" tabindex="-1">' + arr.join('') + '</select></div></td>';

        // Minutes
        var m = (instance._time.minutes < 10 ? '0' : '' ) + instance._time.minutes;
        for (arr = [], i = 0; i < 60; i++) {
            arr.push('<option value="' + i + '"' +
                (i === instance._time.minutes ? ' selected="selected"': '') + '>' +
                (i < 10 ? '0' : '' ) + i + '</option>');
        }
        html += '<td><div class="pikt-label">'+ instance._time.sep +'</div></td><td><div class="pikt-label">' + m + '<select class="pikt-select pikt-select-minutes" tabindex="-1">' + arr.join('') + '</select></div></td>';

        // Seconds
        if (instance._time.hasseconds) {
            var s = (instance._time.seconds < 10 ? '0' : '' ) + instance._time.seconds;
            for (arr = [], i = 0; i < 60; i++) {
                arr.push('<option value="' + i + '"' +
                    (i === instance._time.seconds ? ' selected="selected"': '') + '>' +
                    (i < 10 ? '0' : '' ) + i + '</option>');
            }
            html += '<td><div class="pikt-label">'+ instance._time.sep +'</div></td><td><div class="pikt-label">' + s + '<select class="pikt-select pikt-select-seconds" tabindex="-1">' + arr.join('') + '</select></div></td>';
        }

        // AM/ PM
        if (instance._time.clock12h) {
            var pm = (instance._time.pm ? 'PM' : 'AM' );
            arr = [];
            arr.push('<option value="' + 0 + '"' +
                (false === instance._time.pm ? ' selected="selected"': '') + '>' +
                'AM' + '</option>');
            arr.push('<option value="' + 1 + '"' +
                (true === instance._time.pm ? ' selected="selected"': '') + '>' +
                'PM' + '</option>');
            html += '<td><div class="pikt-label">&nbsp;</div></td><td><div class="pikt-label">' + pm + '<select class="pikt-select pikt-select-pm" tabindex="-1">' + arr.join('') + '</select></div></td>';
        }        

        html += '</tr>';

        return html;
    },

    renderTime = function(instance, randId)
    {

        var html = '<div id="' + randId + '" class="pikt-table"><table cellpadding="0" cellspacing="0" role="grid">';

        html += '<tbody>' + renderIncrRow(instance) + renderTimeRow(instance) + renderDecrRow(instance) + '</body>';

        return html += '</table></div>';
    },

    /**
     * Pikatime constructor
     */
    Pikatime = function(options)
    {
        var self = this,
            opts = self.config(options);

        self._onMouseDown = function(e)
        {
            if (!self._v) {
                return;
            }
            e = e || window.event;
            var target = e.target || e.srcElement;
            if (!target) {
                return;
            }

            if (!hasClass(target, 'is-disabled')) {
                if (hasClass(target, 'pikt-incr-hours')) {
                    self.nextHour();
                } else if (hasClass(target, 'pikt-decr-hours')) {
                    self.prevHour();
                } else if (hasClass(target, 'pikt-incr-minutes')) {
                    self.nextMinute();
                } else if (hasClass(target, 'pikt-decr-minutes')) {
                    self.prevMinute();
                } else if (hasClass(target, 'pikt-incr-seconds')) {
                    self.nextSecond();
                } else if (hasClass(target, 'pikt-decr-seconds')) {
                    self.prevSecond();
                } else if (hasClass(target, 'pikt-incr-pm')) {
                    self.nextPm();
                } else if (hasClass(target, 'pikt-decr-pm')) {
                    self.prevPm();
                }
            }

            if (!hasClass(target, 'pikt-select')) {
                // if this is touch event prevent mouse events emulation
                if (e.preventDefault) {
                    e.preventDefault();
                } else {
                    e.returnValue = false;
                    return false;
                }
            } else {
                self._c = true;
            }
        };

        self._onChange = function(e)
        {
            e = e || window.event;
            var target = e.target || e.srcElement;
            if (!target) {
                return;
            } else if (hasClass(target, 'pikt-select-hours')) {
                self.gotoHour(target.value);
            } else if (hasClass(target, 'pikt-select-minutes')) {
                self.gotoMinute(target.value);
            } else if (hasClass(target, 'pikt-select-seconds')) {
                self.gotoSecond(target.value);
            } else if (hasClass(target, 'pikt-select-pm')) {
                self.gotoPm(target.value);
            }
        };

        self._onKeyChange = function(e)
        {
            e = e || window.event;

            if (self.isVisible()) {

                switch(e.keyCode){
                    case 13:
                    case 27:
                        if (opts.field) {
                            opts.field.blur();
                        }
                        break;
                    case 37:
                        e.preventDefault();
                        self.adjustTime('subtract', 1);
                        break;
                    case 38:
                        self.adjustTime('add', 60);
                        break;
                    case 39:
                        self.adjustTime('add', 1);
                        break;
                    case 40:
                        self.adjustTime('subtract', 60);
                        break;
                }
            }
        };

        self._onInputChange = function(e)
        {
            var time;

            if (e.firedBy === self) {
                return;
            }
            if (opts.format) {
                time = new Date(self.parseTime(self.TimeFmt2Default(opts.field.value, opts.format)));
            } else {
                time = new Date(self.parseTime(opts.field.value));
            }
            if (isDate(time)) {
                self.setTime(time);
            } else {
                opts.field.value = self.toString();
            }

            if (!self._v) {
                self.show();
            }
        };

        self._onInputFocus = function()
        {
            self.show();
        };

        self._onInputClick = function()
        {
            self.show();
        };

        self._onInputBlur = function()
        {
            // IE allows pika div to gain focus; catch blur the input field
            var pEl = document.activeElement;
            do {
                if (hasClass(pEl, 'pikt-single')) {
                    return;
                }
            }
            while ((pEl = pEl.parentNode));

            if (!self._c) {
                self._b = sto(function() {
                    self.hide();
                }, 50);
            }
            self._c = false;
        };

        self._onClick = function(e)
        {
            e = e || window.event;
            var target = e.target || e.srcElement,
                pEl = target;
            if (!target) {
                return;
            }
            if (!hasEventListeners && hasClass(target, 'pikt-select')) {
                if (!target.onchange) {
                    target.setAttribute('onchange', 'return;');
                    addEvent(target, 'change', self._onChange);
                }
            }
            do {
                if (hasClass(pEl, 'pikt-single') || pEl === opts.trigger) {
                    return;
                }
            }
            while ((pEl = pEl.parentNode));
            if (self._v && target !== opts.trigger && pEl !== opts.trigger) {
                self.hide();
            }
        };

        self.el = document.createElement('div');
        self.el.className = 'pikt-single' + (opts.theme ? ' ' + opts.theme : '');

        addEvent(self.el, 'mousedown', self._onMouseDown, true);
        addEvent(self.el, 'touchend', self._onMouseDown, true);
        addEvent(self.el, 'change', self._onChange);
        addEvent(document, 'keydown', self._onKeyChange);

        if (opts.field) {
            if (opts.container) {
                opts.container.appendChild(self.el);
            } else if (opts.bound) {
                document.body.appendChild(self.el);
            } else {
                opts.field.parentNode.insertBefore(self.el, opts.field.nextSibling);
            }
            addEvent(opts.field, 'change', self._onInputChange);

            if (!opts.defaultTime) {
                if (opts.field.value) {
                    opts.defaultTime = new Date(Date.parse(opts.field.value));
                }
                opts.setdefaultTime = true;
            }
        }

        var defDate = opts.defaultTime;

        if (isDate(defDate)) {
            if (opts.setdefaultTime) {
                self.setTime(defDate, true);
            } else {
                self.gotoTime(defDate);
            }
        } else {
            self.gotoTime(new Date());
        }

        if (opts.bound) {
            this.hide();
            self.el.className += ' is-bound';
            addEvent(opts.trigger, 'click', self._onInputClick);
            addEvent(opts.trigger, 'focus', self._onInputFocus);
            addEvent(opts.trigger, 'blur', self._onInputBlur);
        } else {
            this.show();
        }
    };


    /**
     * public Pikatime API
     */
    Pikatime.prototype = {


        /**
         * configure functionality
         */
        config: function(options)
        {
            if (!this._o) {
                this._o = extend({}, defaults, true);
            }

            var opts = extend(this._o, options, true);

            opts.field = (opts.field && opts.field.nodeName) ? opts.field : null;

            opts.theme = (typeof opts.theme) === 'string' && opts.theme ? opts.theme : null;

            opts.bound = !!(opts.bound !== undefined ? opts.field && opts.bound : opts.field);

            opts.trigger = (opts.trigger && opts.trigger.nodeName) ? opts.trigger : opts.field;

            opts.disableWeekends = !!opts.disableWeekends;

            opts.disableDayFn = (typeof opts.disableDayFn) === 'function' ? opts.disableDayFn : null;

            var min = 0;
            var max = 0;
            if (opts.minTime) {
                min = this.Format2Time(opts.minTime);
                if (!isDate(min)) {
                    opts.minTime = false;
                }
            }
            if (opts.maxTime) {
                max = this.Format2Time(opts.maxTime);
                if (!isDate(max)) {
                    opts.maxTime = false;
                }
            }

            if ((opts.minTime && opts.maxTime) && max < min) {
                opts.maxTime = opts.minTime = false;
            }

            if (opts.minTime) {
                this.setMinTime(min);
            }
            if (opts.maxTime) {
                this.setMaxTime(max);
            }

            return opts;
        },

        /**
         * return a formatted string of the current selection (using Moment.js if available)
         */
        toString: function(format)
        {
            var rv = '';
            if (isDate(this._t)) {
                if (format) {
                    rv = this.TimeDefault2Fmt(this.toTimeString(this._t), format);
                } else if (this._o.format) {
                    rv = this.TimeDefault2Fmt(this.toTimeString(this._t), this._o.format);
                } else {
                    rv = this.toTimeString(this._t);
                }
            }
            return (rv);
        },

        setTimeFmt: function(fmttime)
        {
            var time;
            time = this.Format2Time(fmttime);
            
            if (isDate(time)) {
              this.setTime(time);
            } 
        },

        /**
         * return a Date object of the current selection
         */
        getTime: function()
        {
            return isDate(this._t) ? this.toTimeString(new Date(this._t.getTime())) : null;
        },

        /**
         * set the current selection
         */
        setTime: function(time, preventOnSelect)
        {
            if (!time) {
                this._t = null;

                if (this._o.field) {
                    this._o.field.value = '';
                    fireEvent(this._o.field, 'change', { firedBy: this });
                }

                return this.draw();
            }
            if (typeof time === 'string') {
                time = new Date(this.parseTime(time));
            }
            if (!isDate(time)) {
                return;
            }

            var min = this._o.minTime,
                max = this._o.maxTime;

            if (isDate(min) && time < min) {
                time = min;
            } else if (isDate(max) && time > max) {
                time = max;
            }

            this._t = new Date(time.getTime());
            this.gotoTime(this._t);

            if (this._o.field) {
                this._o.field.value = this.toString();
                fireEvent(this._o.field, 'change', { firedBy: this });
            }
            if (!preventOnSelect && typeof this._o.onSelect === 'function') {
                this._o.onSelect.call(this, this.getTime());
            }
        },

        /**
         * change view to a specific time
         */
        gotoTime: function(time)
        {
            if (!isDate(time)) {
                return;
            }

            var clock12h = false;
            var hasseconds = false;
            var sep = ":";
            if (this._o.format) {
                var t = this.TimeDecodeFmt(this._o.format);
                if ((t.hour12pos>-1) || (t.ampmpos>-1)) {
                    clock12h = true;
                }
                if (t.secondspos>-1) {
                    hasseconds = true;
                }
                sep = t.separator;
            }

            var h = 0;
            var pm = false;
            if (clock12h) {
                var r=this.Hours24h_12h(time.getHours());
                pm=r.pm;
                h=r.h;                
            } else {
                h = time.getHours();
            }

            this._time = {
                hours: h,
                minutes: time.getMinutes(),
                seconds: time.getSeconds(),
                pm: pm,
                clock12h: clock12h,
                hasseconds: hasseconds,
                sep: sep
            };

            this.draw();
        },

        adjustTime: function(sign, minutes) {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            var difference = parseInt(minutes)*60*1000;
            var newTime;          

            if (sign === 'add') {
                newTime = new Date(this.modTime(time + difference));
            } else if (sign === 'subtract') {
                newTime = new Date(this.modTime(time - difference));
            }

            this.setTime(newTime);
        },

        /**
         * change view to a specific month (zero-index, e.g. 0: January)
         */
        gotoHour: function(hour)
        {
            if (!isNaN(hour)) { 
                var time = this.decodeTime(new Date(isDate(this._t) ? this._t.getTime() : 0));
                var h = hour;
                if (this._time.clock12h) {
                    h = this.Hours12h_24h(parseInt(hour), this._time.pm);
                }
                this.setTime(this.encodeTime(h,time.m,time.s));
            }
        },

        gotoMinute: function(minute)
        {
            if (!isNaN(minute)) { 
                var time = this.decodeTime(new Date(isDate(this._t) ? this._t.getTime() : 0));
                this.setTime(this.encodeTime(time.h,minute,time.s));
            }            
        },

        gotoSecond: function(second)
        {
            if (!isNaN(second)) { 
                var time = this.decodeTime(new Date(isDate(this._t) ? this._t.getTime() : 0));
                this.setTime(this.encodeTime(time.h,time.m,second));
            } 
        },

        gotoPm: function(pm)
        {
            if (!isNaN(pm)) { 
                if (this._time.clock12h) {
                    if (pm != this._time.pm) {
                        if (pm) { // was AM
                            this.prevPm();
                        } else { // was PM
                            this.nextPm();
                        }
                    }
                }
            }       
        },

        nextHour: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time + 60*60*1000)));
        },

        prevHour: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time - 60*60*1000)));
        },

        nextMinute: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time + 60*1000)));
        },

        prevMinute: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time - 60*1000)));
        },

        nextSecond: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time + 1000)));
        },

        prevSecond: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time - 1000)));
        },

        nextPm: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time + 12*60*60*1000)));
        },

        prevPm: function()
        {
            var time = isDate(this._t) ? this._t.getTime() : 0;
            this.setTime(new Date(this.modTime(time - 12*60*60*1000)));
        },

        modTime: function(time) {
            var day = (24*60*60*1000);
            if (time > day-1) {
                time -= (day);
            } else if (time < 0) {
                time += day;
            }
            return (time);
        },

        decodeTime: function(time) {
            var td = {
                    h: 0,
                    m: 0,
                    s: 0
                };
            if(time instanceof Date) {
                td= {
                    h: time.getHours(),
                    m: time.getMinutes(),
                    s: time.getSeconds()
                };
            }

            return td;
        },

        encodeTime: function(h, m, s) {
            return new Date(Date.parse("1-1-1970 "+h+":"+m+":"+s));
        },

        /**
         * change the minTime
         */
        setMinTime: function(value)
        {
            if(value instanceof Date) {
                this._o.minTime = value;
                this._o.minHour  = value.getHours();
                this._o.minMinutes = value.getMinutes();
                this._o.minSeconds = value.getSeconds();
            } else {
                this._o.minTime = defaults.minTime;
                this._o.minHour  = value.MinHour;
                this._o.minMinutes = value.minMinutes;
                this._o.minSeconds = value.minSeconds;
                this._o.startRange = defaults.startRange;
            }

            this.draw();
        },

        /**
         * change the maxDate
         */
        setMaxTime: function(value)
        {
            if(value instanceof Date) {
                this._o.maxTime = value;
                this._o.maxHour  = value.getHours();
                this._o.maxMinutes = value.getMinutes();
                this._o.maxSeconds = value.getSeconds();
            } else {
                this._o.maxTime = defaults.maxTime;
                this._o.maxHour  = value.MaxHour;
                this._o.maxMinutes = value.maxMinutes;
                this._o.maxSeconds = value.maxSeconds;
                this._o.endRange = defaults.endRange;
            }

            this.draw();
        },

        TimeFmt2Default: function(timefmt, fmt) {
            var fmtdecoded = this.TimeDecodeFmt(fmt);
            var h = "00";
            var m = "00";
            var s = "00";

            var timearray = timefmt.split(fmtdecoded.separator).join(' ').split(' ');

            if (fmtdecoded.hour12pos >= 0) {
                var pm = true;
                if (fmtdecoded.ampmpos >= 0) {
                    if (timearray[fmtdecoded.ampmpos] == "AM") {
                        pm = false;
                    }
                }
                var ih = this.Hours12h_24h(parseInt(timearray[fmtdecoded.hour12pos]),pm);
                h = (ih < 10 ? '0' : '' )+ ih;
            }
            if (fmtdecoded.hour24pos >= 0) {
                h = timearray[fmtdecoded.hour24pos];
            }
            if (fmtdecoded.minutepos >= 0) {
                m = timearray[fmtdecoded.minutepos];
            }
            if (fmtdecoded.secondspos >= 0) {
                s = timearray[fmtdecoded.secondspos];
            }
            // datepicker expects hms
            return h + ":" + m + ":" + s;
        },

        TimeDefault2Fmt: function(timedefault, fmt) {
            var retval = "";
            var fmtdecoded = this.TimeDecodeFmt(fmt);
            var d=new Date("1-1-1970 "+timedefault);
            var pm=false;
            for (var i=0; i<4; i++) {
                if (fmtdecoded.hour12pos == i) {
                    var r=this.Hours24h_12h(d.getHours());
                    pm=r.pm;
                    retval += (r.h < 10 ? '0' : '' ) + r.h;
                }
                if (fmtdecoded.hour24pos == i) {
                    retval += (d.getHours() < 10 ? '0' : '' ) + d.getHours();
                }
                if (fmtdecoded.minutepos == i) {
                    retval += fmtdecoded.separator + (d.getMinutes() < 10 ? '0' : '' ) + d.getMinutes();
                }
                if (fmtdecoded.secondspos == i) {
                    retval += fmtdecoded.separator + (d.getSeconds() < 10 ? '0' : '' ) + d.getSeconds();
                }
                if (fmtdecoded.ampmpos == i) {
                    if (pm) {
                        retval += " PM";
                    } else {
                        retval += " AM";
                    }
                }
            }
            return retval;
        },

        Hours24h_12h: function(h) {
            var pm=false;
            if (h==0) {
                h = 12;
            } else if (h==12) {
                pm=true;
            } else if (h>12) {
                h -= 12;
                pm=true;
            }

            return {
                h: h,
                pm: pm
            };
        },

        Hours12h_24h: function(h, pm) {
            if (pm) {
                if (h < 12) {
                    h += 12;
                }
            } else { // AM
                if (h == 12) {
                    h = 0;
                }            
            }

            return h;
        },

        TimeDecodeFmt: function(fmt) {
            var separator = "?";
            var hour12pos = -1;
            var hour24pos = -1;
            var minutepos = -1;
            var secondspos = -1;
            var ampmpos = -1;
            // "%T" "%H:%M:%S" "%I:%M %p"
            // %H  Hour (24-hour clock) as a decimal number [00,23].    
            // %I  Hour (12-hour clock) as a decimal number [01,12].
            // %M  Minute as a decimal number [00,59].  
            // %p  Locale’s equivalent of either AM or PM.
            // %S  Second as a decimal number [00,61].
            // %T - current time, equal to %H:%M:%S
            // %r - time in a.m. and p.m. notation
            // %R - time in 24 hour notation

            // replace %T by %H:%M:%S for better processing
            fmt = fmt.replace("%T", "%H:%M:%S").replace("%R", "%H:%M:%S").replace("%r", "%I:%M:%S %p");

            if (fmt.indexOf(":") >=0 ) {
                separator = ":";
            } else if (fmt.indexOf(".") >=0 ) {
                separator = ".";
            }

            var fmtarray = fmt.split(separator).join(' ').split(' ');
            for (var i in fmtarray) {
                if (fmtarray[i] == "%I") {
                    hour12pos = i;
                } else if (fmtarray[i] == "%H") {
                    hour24pos = i;
                } else if (fmtarray[i] == "%M") {
                    minutepos = i;
                } else if (fmtarray[i] == "%S") {
                    secondspos = i;
                } else if (fmtarray[i] == "%p") {
                    ampmpos = i;
                } 
            }

            return {
                separator: separator,
                hour12pos: hour12pos,
                hour24pos: hour24pos,
                minutepos: minutepos,
                secondspos: secondspos,
                ampmpos: ampmpos
            };
        },

        Format2Time: function(fmttime)
        {
            var time;
            if (this._o.format) {
                time = new Date(this.parseTime(this.TimeFmt2Default(fmttime, this._o.format)));
            } else {
                time = new Date(this.parseTime(fmttime));
            }
            return (time); 
        },

        parseTime: function(deftime) {
            return Date.parse("1-1-1970 "+deftime);
        },

        toTimeString: function(time) {
            return(time.toTimeString().split(' ')[0]);
        },

        /**
         * refresh the HTML
         */
        draw: function(force)
        {
            if (!this._v && !force) {
                return;
            }
            var opts = this._o,
                html = '',
                randId;

            randId = 'pikt-title-' + Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 2);
            html += '<div class="pikt-time">' + renderTime(this, randId) + '</div>';

            this.el.innerHTML = html;

            if (opts.bound) {
                if(opts.field.type !== 'hidden') {
                    sto(function() {
                        opts.trigger.focus();
                    }, 1);
                }
            }

            if (typeof this._o.onDraw === 'function') {
                this._o.onDraw(this);
            }

            if (opts.bound) {
                // let the screen reader user know to use arrow keys
                opts.field.setAttribute('aria-label', 'Use the arrow keys to pick a date');
            }
        },

        adjustPosition: function()
        {
            var field, pEl, width, height, viewportWidth, viewportHeight, scrollTop, left, top, clientRect;

            if (this._o.container) return;

            this.el.style.position = 'absolute';

            field = this._o.trigger;
            pEl = field;
            width = this.el.offsetWidth;
            height = this.el.offsetHeight;
            viewportWidth = window.innerWidth || document.documentElement.clientWidth;
            viewportHeight = window.innerHeight || document.documentElement.clientHeight;
            scrollTop = window.pageYOffset || document.body.scrollTop || document.documentElement.scrollTop;

            if (typeof field.getBoundingClientRect === 'function') {
                clientRect = field.getBoundingClientRect();
                left = clientRect.left + window.pageXOffset;
                top = clientRect.bottom + window.pageYOffset;
            } else {
                left = pEl.offsetLeft;
                top  = pEl.offsetTop + pEl.offsetHeight;
                while((pEl = pEl.offsetParent)) {
                    left += pEl.offsetLeft;
                    top  += pEl.offsetTop;
                }
            }

            // default position is bottom & left
            if ((this._o.reposition && left + width > viewportWidth) ||
                (
                    this._o.position.indexOf('right') > -1 &&
                    left - width + field.offsetWidth > 0
                )
            ) {
                left = left - width + field.offsetWidth;
            }
            if ((this._o.reposition && top + height > viewportHeight + scrollTop) ||
                (
                    this._o.position.indexOf('top') > -1 &&
                    top - height - field.offsetHeight > 0
                )
            ) {
                top = top - height - field.offsetHeight;
            }

            this.el.style.left = left + 'px';
            this.el.style.top = top + 'px';
        },

        isVisible: function()
        {
            return this._v;
        },

        show: function()
        {
            if (!this.isVisible()) {
                this._v = true;
                this.draw();
                if (this._o.bound) {
                    addEvent(document, 'click', this._onClick);
                    this.adjustPosition();
                }
                removeClass(this.el, 'is-hidden');
                if (typeof this._o.onOpen === 'function') {
                    this._o.onOpen.call(this);
                }
            }
        },

        hide: function()
        {
            var v = this._v;
            if (v !== false) {
                if (this._o.bound) {
                    removeEvent(document, 'click', this._onClick);
                }
                this.el.style.position = 'static'; // reset
                this.el.style.left = 'auto';
                this.el.style.top = 'auto';
                addClass(this.el, 'is-hidden');
                this._v = false;
                if (v !== undefined && typeof this._o.onClose === 'function') {
                    this._o.onClose.call(this);
                }
            }
        },

        /**
         * GAME OVER
         */
        destroy: function()
        {
            this.hide();
            removeEvent(this.el, 'mousedown', this._onMouseDown, true);
            removeEvent(this.el, 'touchend', this._onMouseDown, true);
            removeEvent(this.el, 'change', this._onChange);
            if (this._o.field) {
                removeEvent(this._o.field, 'change', this._onInputChange);
                if (this._o.bound) {
                    removeEvent(this._o.trigger, 'click', this._onInputClick);
                    removeEvent(this._o.trigger, 'focus', this._onInputFocus);
                    removeEvent(this._o.trigger, 'blur', this._onInputBlur);
                }
            }
            if (this.el.parentNode) {
                this.el.parentNode.removeChild(this.el);
            }
        }

    };

    return Pikatime;

}));