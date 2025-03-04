import re
import time
import weakref
from .fclasses import *
from .constants import EngineEvTypes


_FIRST_LISTENER_ID = 72931


def game_events_enum(x_iterable):
    return PseudoEnum(x_iterable, 1 + EngineEvTypes.first + EngineEvTypes.size)


@Singleton
class EvManager:
    def __init__(self):
        self._etype_to_listenerli = dict()
        self._cbuffer = CircularBuffer()
        self._known_ev_types = dict()  # corresp nom event camelcase <-> identifiant num.
        self._etype_to_sncname = dict()  # corresp identifiant num. <-> nom event snakecase
        self.regexp = None
        self.debug_mode = False
        self.a_event_source = None
        # for debug purpose
        self._cached_extra_penum = None

        # can be useful when one needs to insta-STOP processing events(use-case: reset the manager)
        self.fresh_reset = False

        # for auto-repeat post event mechanism (like in JS, set_interval):
        self._lsent = dict()  # etype <-> t
        self._intervalsdef = dict()
        self._storedargs = dict()  # etype <-> dict kwargs

    @property
    def all_possible_etypes(self):
        return tuple(self._known_ev_types.keys())

    @property
    def queue_size(self):
        return self._cbuffer.get_size()

    def post(self, etype, **kwargs):
        t = int(etype)  # ~= assert its an int that is posted
        self._cbuffer.enqueue((etype, kwargs))

    def set_interval(self, delay, etype, **kwargs):
        """
        :param delay: in MS !!!!
        :param etype:
        :param kwargs:
        :return:
        """
        if delay > 0:
            self._intervalsdef[etype] = delay/1000  # to keep seconds
            self._storedargs[etype] = kwargs
            # pretend one was sent right now
            self._lsent[etype] = time.time()
            print('set_interval OK')
            print(self._intervalsdef, self._storedargs, self._lsent)
        else:
            del self._intervalsdef[etype]

    def update(self):
        # optional block:
        # in some cases this is equivalent to a <pass> instruction
        if self.a_event_source is not None:
            self._cbuffer.deque_obj.extend(self.a_event_source.fetch_kengi_events())

        # if some interval timed-events have been defined, inject whats needed to _cbuffer
        for ety, delay in self._intervalsdef.items():
            tnow = time.time()
            dt = tnow-self._lsent[ety]
            if dt > delay:
                kwargs = self._storedargs[ety]
                # 'pushin to cbuffer:', ety, kwargs, ' and dt was:', dt)
                self.post(ety, **kwargs)
                self._lsent[ety] = tnow

        # process all content tbf in ._cbuffer
        kappa = len(self._cbuffer.deque_obj)
        while kappa > 0:
            etype, d = self._cbuffer.dequeue()
            kappa -= 1
            if etype not in self._etype_to_listenerli:
                continue
            for lobj in self._etype_to_listenerli[etype]:
                if hasattr(lobj, 'on_event'):  # on_event defined => we always use this method!
                    lobj.on_event(KengiEv(etype, **d))
                else:
                    adhoc_meth_name = 'on_'+self._etype_to_sncname[etype]
                    getattr(lobj, adhoc_meth_name)(KengiEv(etype, **d))
            if self.fresh_reset:
                return

    def hard_reset(self):
        self.fresh_reset = True

        # destroy events
        self._cbuffer = CircularBuffer()

        self._etype_to_listenerli.clear()

        self._lsent = dict()  # etype <-> t
        self._intervalsdef = dict()
        self._storedargs = dict()  # etype <-> dict kwargs

    def _refresh_regexp(self, gnames):
        # we create a regexp such that, listeners know what keywords they have to consider
        # when analysing the list of their
        # .on_***
        # attribute methods
        regexp_prefix = '^on_(?:'
        rxp_body = '|'.join(gnames)
        regexp_sufix = '$)'
        # debug: print the updated regexp
        # -
        # print(regexp_prefix + rxp_body + regexp_sufix)
        self.regexp = re.compile(regexp_prefix + rxp_body + regexp_sufix)

    def subscribe(self, ename, listener_obj):
        cod = self._known_ev_types[ename]
        if cod not in self._etype_to_listenerli:
            self._etype_to_listenerli[cod] = list()

        self._etype_to_listenerli[cod].append(listener_obj)
        if self.debug_mode:
            print('  debug SUBSCRIBE - - - {} - {}'.format(ename, listener_obj))

    def unsubscribe(self, ename, listener_obj):
        cod = self._known_ev_types[ename]
        # if cod in self._etype_to_listenerli:
        try:
            self._etype_to_listenerli[cod].remove(listener_obj)
        except (KeyError, ValueError):
            print('***EvManager warning. Trying to remove listener_obj {}, not found!'.format(
                listener_obj.id
            ))
        if self.debug_mode:
            print('  debug UNSUBSCRIBE - - - {} - {}'.format(ename, listener_obj))

    def inspect_etype(self, g_etype):
        if self._cached_extra_penum:
            if g_etype in self._cached_extra_penum.inv_map:
                return self._cached_extra_penum.inv_map[g_etype]
        return EngineEvTypes.inv_map[g_etype]

    def setup(self, given_extra_penum=None):
        self.fresh_reset = False

        names = list()
        self._known_ev_types = EngineEvTypes.content.copy()

        for evname, eid in EngineEvTypes.content.items():
            names.append(to_snakecase(evname))

        if given_extra_penum is None:
            self._cached_extra_penum = None
        else:
            self._cached_extra_penum = given_extra_penum
            self._known_ev_types.update(given_extra_penum.content)
            for evname, eid in given_extra_penum.content.items():
                names.append(to_snakecase(evname))

        # force a {refresh regexp} op!
        self._refresh_regexp(names)

        for ename_cc, etype in self._known_ev_types.items():
            self._etype_to_sncname[etype] = to_snakecase(ename_cc)


class Emitter:
    __free_id = _FIRST_LISTENER_ID

    def __init__(self):
        self._manager = None
        self._lid = Emitter.__free_id
        Emitter.__free_id = Emitter.__free_id + 1

    def pev(self, evtype, **kwargs):
        if self._manager is None:
            self._manager = EvManager.instance()
        self._manager.post(evtype, **kwargs)


class EvListener(Emitter):
    _index_obj = dict()

    def __init__(self):
        super().__init__()
        self._is_active = False
        self._inspection_res = set()
        self._tracked_ev = list()
        print('creation listener', self._lid)

    @property
    def active(self):
        return self._is_active

    @property
    def id(self):
        return self._lid

    @classmethod
    def lookup(cls, ident):
        """
        returns None if no listener that has `ident` as an identifier, has called .bind()
        the ad-hoc listener otherwise
        """
        try:
            return cls._index_obj[ident]
        except KeyError:
            return None

    def bind(self):
        self.__class__._index_obj[self.id] = self
        return self.id

    def turn_on(self):
        if self._is_active:
            raise ValueError('call turn_on on obj {} where ._is_active is already True!'.format(self))

        if self._manager is None:
            self._manager = EvManager.instance()

        # special case: listen to every possible event!
        card_sub_op = 0
        if hasattr(self, 'on_event') and callable(self.on_event):
            petypes = self._manager.all_possible_etypes
            for etn in petypes:
                self._tracked_ev.append(etn)
                card_sub_op += 1

        else:
            # introspection & detection des on_* ... où le caractère étoile
            # signifie tt type d'évènement connu du moteur, que ce soit un event engine ou un event custom ajouté
            every_method = [method_name for method_name in dir(self) if callable(getattr(self, method_name))]
            callbacks_only = [mname for mname in every_method if self._manager.regexp.match(mname)]

            # let's PRINT crucial WARNING messages, if there is a on_unknwEvent found
            for e in every_method:
                if e[:3] == 'on_' and (e not in callbacks_only):
                    rawmsg = '!!! BIG WARNING !!!\n    listener #{} that is{}\n'
                    rawmsg += '    has been turned -ON- but its method "{}" cannot be called (Unknown event type)'
                    w_msg = rawmsg.format(self.id, self, e)
                    print(w_msg)

            for cbname in callbacks_only:
                # remove 'on_' prefix and convert Back to CamlCase
                self._tracked_ev.append(to_camelcase(cbname[3:]))
            card_sub_op += len(callbacks_only)

        # -- done counting sub_op ---
        if card_sub_op > 0:
            self._is_active = True
            # enregistrement de son activité d'écoute auprès du evt manager
            for evname in self._tracked_ev:
                self._manager.subscribe(evname, self)
        else:
            print('***WARNING: non-valid turn_on operation, class:', self.__class__, 'cannot find valid on_* methods')

    def turn_off(self):
        # opération contraire
        for evname in self._tracked_ev:
            self._manager.unsubscribe(evname, self)
        del self._tracked_ev[:]
        self._is_active = False
