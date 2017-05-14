(function($) {

    var opts = ['raw', 'half', 'double', 'blend', 'flat', 'blur3', 'blur30', 'fast', 'slow'];
    var opt_speed_change = {
        'fast': 2,
        'slow': 0.6
    };

    $.StoryWidget = function(sess_dir) {
        this.$el = document.createElement("div");
        this.$el.className = "storywidget";
        this.$el.innerHTML = "Loading...";

        this.sess_dir = sess_dir;

        this.cur_opt_idx = 0;   // XXX: Take in as param

        this.fetch_transcript();
    }
    $.StoryWidget.prototype.fetch_transcript = function() {
        this.xhr = new XMLHttpRequest();
        this.xhr.open("GET", this.sess_dir + 'align.json', true);
        this.xhr.onload = function() {
            this.$el.innerHTML = "";
            this.align = JSON.parse(this.xhr.responseText);
            this.render();
        }.bind(this);
        this.xhr.send();
    }
    $.StoryWidget.prototype.render = function() {
        this.render_opts();
        this.render_audio();
        this.render_words();
    }
    $.StoryWidget.prototype.set_audio_source = function() {
        this.$a.src = this.sess_dir + opts[this.cur_opt_idx] + '.mp3';
        this.opts$.forEach(function($o,idx) {
            if(idx == this.cur_opt_idx) {
                $o.className = "active opt";
            }
            else {
                $o.className = "opt";
            }
        }, this)
    }
    $.StoryWidget.prototype.render_words = function() {
        var p_wd = null;

        this.words$ = [];
        this.$transcript = document.createElement("div");
        this.$transcript.className = "transcript";
        this.$el.appendChild(this.$transcript);

        this.align.words
            .forEach(function(wd) {
                // XXX: Insert punctuation

                var $el = document.createElement("span");
                $el.textContent = wd.word + " ";
                $el.className = "word";
                $el.onclick = function() {
                    this.$a.currentTime = wd.start / (opt_speed_change[opts[this.cur_opt_idx]] || 1);
                    this.$a.play();
                }.bind(this)
                this.$transcript.appendChild($el);
                
                this.words$.push({
                    $el: $el,
                    wd: wd
                })

                p_wd = wd;
            }, this)

    }
    $.StoryWidget.prototype.render_audio = function() {
        this.$a = document.createElement("audio");
        this.set_audio_source();
        this.$a.controls = "controls";
        this.$el.appendChild(this.$a);
    }
    $.StoryWidget.prototype.render_opts = function() {
        this.$opts = document.createElement("div");
        this.$el.appendChild(this.$opts);
        this.$opts.className = "opts";
        
        this.opts$ = [];
        opts.forEach(function(name, idx) {
            var $opt = document.createElement("div");
            $opt.textContent = name;
            $opt.className = "opt";
            $opt.onclick = function() {
                this.cur_opt_idx = idx;
                this.set_audio_source();
            }.bind(this);
            this.opts$.push($opt);
            this.$opts.appendChild($opt);
        }, this)
    }
    $.StoryWidget.prototype.tick = function() {
        if(!this.$a) {
            return;
        }
        
        var t = this.$a.currentTime / (opt_speed_change[opts[this.cur_opt_idx]] || 1);

        var cur_wd;
        this.words$.forEach(function(obj) {
            if(obj.wd.start <= t && obj.wd.end >= t) {
                cur_wd = obj;
            }
        })
        if(cur_wd != this._cur_wd) {
            if(this._cur_wd) {
                this._cur_wd.$el.className = "word"
            }
            if(cur_wd) {
                cur_wd.$el.className = "active word"
            }
            
            this._cur_wd = cur_wd;
        }
    }

})(window);
