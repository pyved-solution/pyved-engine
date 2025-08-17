from .EvManager import EvManager
from ..concr_engin.pe_vars import EngineEvTypes, PseudoEnum
from ..concr_engin.pe_vars import to_camelcase


_FIRST_LISTENER_ID = 72931


def game_events_enum(x_iterable):
    return PseudoEnum(x_iterable, 1 + EngineEvTypes.first + EngineEvTypes.size)


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
