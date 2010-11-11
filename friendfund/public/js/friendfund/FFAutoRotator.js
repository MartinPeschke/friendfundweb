dojo.provide("friendfund.FFAutoRotator");
dojo.require("dojox.widget.AutoRotator");
dojo.require("dojox.widget.rotator.Pan");

(function(d){

	d.declare("friendfund.FFAutoRotator", dojox.widget.AutoRotator, {
		constructor: function(){
			//	summary:
			//		Initializes the timer and connect to the rotator.

			var _t = this;

			// validate the cycles counter
			if(_t.cycles-0 == _t.cycles && _t.cycles > 0){
				// we need to add 1 because we decrement cycles before the animation starts
				_t.cycles++;
			}else{
				_t.cycles = _t.cycles ? -1 : 0;
			}
			_t.ffTransition = dojox.widget.rotator.panLeft();
			_t.rwdTransition = dojox.widget.rotator.panRight();
			// wire up the mouse hover events
			_t._connects = [
				d.connect(_t._domNode, "onmouseover", function(){
					// temporarily suspend the cycling, but don't officially pause
					// it and don't allow suspending if we're transitioning
					if(_t.suspendOnHover && !_t.anim && !_t.wfe){
						var t = _t._endTime,
							n = _t._now();
						_t._suspended = true;
						_t._resetTimer();
						_t._resumeDuration = t > n ? t - n : 0.01;
					}
				}),

				d.connect(_t._domNode, "onmouseout", function(){
					// if we were playing, resume playback unless were in the
					// middle of a transition
					if(_t.suspendOnHover && !_t.anim){
						_t._suspended = false;
						if(_t.playing && !_t.wfe){
							_t.play(true);
						}
					}
				})
			];

			// everything is ready, so start
			if(_t.autoStart && _t.panes.length > 1){
				// start playing
				_t.play();
			}else{
				// since we're not playing, lets pause
				_t.pause();
			}
		},
		next: function(){
			//	summary:
			//		Transitions the Rotator to the next pane.
			return this.go(this.idx + 1, 1);
		},

		prev: function(){
			//	summary:
			//		Transitions the Rotator to the previous pane.
			return this.go(this.idx - 1, -1);
		},
		
		go: function(/*int|string?*/p, /*int*/ffrwd){
			//	summary:
			//		Transitions the Rotator to the specified pane index.
			var _t = this,
				i = _t.idx,
				pp = _t.panes,
				len = pp.length,
				idm = _t._idMap[p];

			// we gotta move on, so if the current pane is waiting for an event, just
			// ignore it and clean up
			_t._resetWaitForEvent();

			// determine the next index and set it to idx for the next go to
			p = idm != null ? idm : (p || 0);
			p = p < len ? (p < 0 ? len-1 : p) : 0;

			// if we're already on the requested pane or still transitioning, then return
			if(p == i || _t.anim){
				return null;
			}

			// get the current and next panes
			var current = pp[i],
				next = pp[p];

			// adjust the zIndexes so our animations look good... this must be done before
			// the animation is created so the animation could override it if necessary
			d.style(current.node, _zIndex, 2);
			d.style(next.node, _zIndex, 1);

			// info object passed to animations and onIn/Out events
			var info = {
					current: current,
					next: next,
					rotator: _t
				},

				// get the transition
				
				var anim = null;
				if(!ffrwd){
					anim = _t._transitions[next.trans];
				} else if(ffrwd>0){
					anim = _t.ffTransition;
				} else if(ffrwd<0){
					anim = _t.rwdTransition;
				}
				anim = _t.anim = anim(d.mixin({
						rotatorBox: _t._domNodeContentBox
					}, info, next.params));
				

			if(anim){
				// create the deferred that we'll be returning
				var def = new d.Deferred(),
					ev = next.waitForEvent,

					h = d.connect(anim, "onEnd", function(){
						// reset the node styles
						d.style(current.node, {
							display: _noneStr,
							left: 0,
							opacity: 1,
							top: 0,
							zIndex: 0
						});

						d.disconnect(h);
						_t.anim = null;
						_t.idx = p;

						// fire end events
						if(current.onAfterOut){ current.onAfterOut(info); }
						if(next.onAfterIn){ next.onAfterIn(info); }

						_t.onUpdate("onAfterTransition");

						if(!ev){
							// if there is a previous waitForEvent, then we need to make
							// sure it gets unsubscribed
							_t._resetWaitForEvent();

							// animation is all done, fire the deferred callback.
							def.callback();
						}
					});

				// if we're waiting for an event, subscribe to it so we know when to continue
				_t.wfe = ev ? d.subscribe(ev, function(){
					_t._resetWaitForEvent();
					def.callback(true);
				}) : null;

				_t.onUpdate("onBeforeTransition");

				// fire start events
				if(current.onBeforeOut){ current.onBeforeOut(info); }
				if(next.onBeforeIn){ next.onBeforeIn(info); }

				// play the animation
				anim.play();

				// return the deferred
				return def; /*Deferred*/
			}
		}
	});

})(dojo);












