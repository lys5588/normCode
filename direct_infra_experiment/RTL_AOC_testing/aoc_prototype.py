from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict, Tuple, Union

# --- AOC Core Abstractions ---

@dataclass
class Event:
    """Represents a discrete event in time."""
    signal: str
    value: Any = None # Can be a primitive or a dict/payload
    time: int = 0

    def __repr__(self):
        val_str = f"={self.value}" if self.value is not None else ""
        return f"@{self.time}: {self.signal}{val_str}"

Bindings = Dict[str, Any]

class Condition:
    """Base class for Triggers and Obligations."""
    def matches(self, event: Event, context: Bindings) -> Tuple[bool, Bindings]:
        """
        Checks if the event matches this condition within the given context.
        Returns:
            (is_match, new_bindings_found)
        """
        raise NotImplementedError

@dataclass
class Signal(Condition):
    """
    Matches a signal name and optionally its value or payload fields.
    
    Args:
        name: The signal name to match.
        value: Exact value to match (if primitive), or subset of fields to match (if dict).
        binds: List of payload keys to bind to context variables (e.g. ['iid'] binds event.value['iid'] to 'iid').
               Can also be a dict {context_var: payload_key}.
        match_binds: List of payload keys that MUST match existing context variables.
                     Can also be a dict {payload_key: context_var}.
    """
    name: str
    value: Any = None
    binds: Union[List[str], Dict[str, str]] = field(default_factory=list)
    match_binds: Union[List[str], Dict[str, str]] = field(default_factory=list)

    def matches(self, event: Event, context: Bindings) -> Tuple[bool, Bindings]:
        if event.signal != self.name:
            return False, {}

        # 1. Check strict value match if provided
        if self.value is not None:
            if isinstance(self.value, dict) and isinstance(event.value, dict):
                # Subset match
                for k, v in self.value.items():
                    if event.value.get(k) != v:
                        return False, {}
            elif event.value != self.value:
                return False, {}

        # 2. Check context constraints (match_binds)
        # e.g. match_binds=['granule'] -> event.value['granule'] == context['granule']
        if self.match_binds:
            if not isinstance(event.value, dict):
                return False, {} # Content matching requires a dict payload
            
            mapping = self.match_binds
            if isinstance(mapping, list):
                mapping = {k: k for k in mapping}
            
            for payload_key, ctx_var in mapping.items():
                if ctx_var not in context:
                    # Should this be an error or just fail match? 
                    # Usually if we depend on a context var that isn't there, strict failure check implies we can't verify.
                    # But for now, let's say it doesn't match.
                    return False, {}
                
                if event.value.get(payload_key) != context[ctx_var]:
                    return False, {}

        # 3. Extract bindings
        new_bindings = {}
        if self.binds:
            if not isinstance(event.value, dict):
                 # If we try to bind from non-dict, maybe we bind the whole value?
                 # Assume dict for named bindings for now.
                 pass
            else:
                mapping = self.binds
                if isinstance(mapping, list):
                   mapping = {k: k for k in mapping}
                
                for ctx_var, payload_key in mapping.items():
                    if payload_key in event.value:
                        new_bindings[ctx_var] = event.value[payload_key]
        
        return True, new_bindings

@dataclass
class AnyOf(Condition):
    conditions: List[Condition]

    def __init__(self, *conditions):
        self.conditions = list(conditions)

    def matches(self, event: Event, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        for cond in self.conditions:
            match, bindings = cond.matches(event, context)
            if match:
                return True, bindings
        return False, {}

@dataclass
class TimingConstraint:
    min_cycles: int = 0
    max_cycles: Optional[int] = None

class RuleStatus:
    PENDING = "PENDING"     
    SATISFIED = "SATISFIED" 
    VIOLATED = "VIOLATED"   
    CANCELLED = "CANCELLED" 

@dataclass
class ActiveRule:
    """An instance of a rule being tracked with specific context."""
    rule_name: str
    start_time: int
    deadline: Optional[int]
    obligation: Condition
    abort: Optional[Condition]
    context: Bindings

    def __repr__(self):
        ctx_str = f" {self.context}" if self.context else ""
        deadline_str = f" (Deadline: {self.deadline})" if self.deadline else ""
        return f"<ActiveRule '{self.rule_name}'{ctx_str} started @{self.start_time}{deadline_str}>"

class Rule:
    def __init__(self, name: str):
        self.name = name
        self._trigger: Optional[Condition] = None
        self._obligation: Optional[Condition] = None
        self._timing: TimingConstraint = TimingConstraint()
        self._abort: Optional[Condition] = None

    def when(self, condition: Condition):
        self._trigger = condition
        return self

    def require(self, condition: Condition):
        self._obligation = condition
        return self
    
    # Alias for readability in chains like .if_followed_by() -> not impl here but conceptually
    def if_followed_by(self, condition: Condition):
        # In current simple model, we assume trigger -> obligation.
        # Complex multi-stage triggers (Trigger A -> Trigger B -> Obligation) need a state machine or composed conditions.
        # For the LR/SC example: Trigger(LR).require(ObligationSC)
        # But the example said: Trigger(LR).if_followed_by(Store).require(Fail)
        # That's a conditional obligation.
        # Let's keep it simple: Trigger(LR) -> Obligation(SC matches Fail IF Store happened? No...)
        # The worked example actually proposed:
        # Obligation: If conflicting store, then SC must fail.
        # This implies a complex obligation: (Store -> SC_Fail)
        # We'll approximate this by supporting complex conditions if needed, or stick to the simple structure for now.
        pass 

    def within(self, cycles: int):
        self._timing.max_cycles = cycles
        return self

    def unless(self, condition: Condition):
        self._abort = condition
        return self

class AOCMonitor:
    def __init__(self):
        self.rules: List[Rule] = []
        self.active_instances: List[ActiveRule] = []
        self.history: List[str] = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def log(self, message: str):
        self.history.append(message)

    def process_event(self, event: Event):
        # 1. Check for Triggers for new instances
        for rule in self.rules:
            if rule._trigger:
                is_match, bindings = rule._trigger.matches(event, {})
                if is_match:
                    deadline = event.time + rule._timing.max_cycles if rule._timing.max_cycles else None
                    instance = ActiveRule(
                        rule_name=rule.name,
                        start_time=event.time,
                        deadline=deadline,
                        obligation=rule._obligation,
                        abort=rule._abort,
                        context=bindings
                    )
                    self.active_instances.append(instance)
                    self.log(f"[{event.time}] RULE '{rule.name}' TRIGGERED by {event.signal} | Context: {bindings}")

        # 2. Check active instances
        remaining_instances = []
        for instance in self.active_instances:
            status = RuleStatus.PENDING

            # Check Abort
            if instance.abort:
                is_abort, _ = instance.abort.matches(event, instance.context)
                if is_abort:
                    status = RuleStatus.CANCELLED
                    self.log(f"[{event.time}] RULE '{instance.rule_name}' CANCELLED by {event.signal} | Context: {instance.context}")
                    continue 

            # Check Obligation
            if instance.obligation:
                is_satisfied, _ = instance.obligation.matches(event, instance.context)
                if is_satisfied:
                    status = RuleStatus.SATISFIED
                    self.log(f"[{event.time}] RULE '{instance.rule_name}' SATISFIED by {event.signal} | Context: {instance.context}")
                    continue 

            # Check Timeout (simulated)
            if instance.deadline is not None and event.time > instance.deadline:
                status = RuleStatus.VIOLATED
                self.log(f"[{event.time}] RULE '{instance.rule_name}' VIOLATED (Timeout) | Context: {instance.context}. Deadline was {instance.deadline}")
                continue 

            remaining_instances.append(instance)
        
        self.active_instances = remaining_instances

    def check_timeouts(self, current_time: int):
        """Force check for timeouts."""
        remaining_instances = []
        for instance in self.active_instances:
            if instance.deadline is not None and current_time > instance.deadline:
                 self.log(f"[{current_time}] RULE '{instance.rule_name}' VIOLATED (Timeout) | Context: {instance.context}. Deadline was {instance.deadline}")
            else:
                remaining_instances.append(instance)
        self.active_instances = remaining_instances

# --- Demos ---

def run_demo():
    print("Investigating AOC Prototype (Enhanced)...")
    monitor = AOCMonitor()

    # --- Scenario 1: Instruction Resolution with Binding ---
    # C001: Instr issued -> Commit or Trap within 100 cycles.
    
    r_c001 = (
        Rule("C001_InstrResolution")
        .when(Signal("instr_issued", binds=["iid"]))
        .require(AnyOf(
            Signal("commit", match_binds=["iid"]),
            Signal("trap", match_binds=["iid"])
        ))
        .within(100)
    )
    monitor.add_rule(r_c001)

    print("\n--- Example 1: Instruction Resolution ---")
    
    events = [
        Event("instr_issued", {"iid": 0x42, "op": "ADD"}, 100),
        Event("instr_issued", {"iid": 0x43, "op": "SUB"}, 105),
        Event("commit", {"iid": 0x43}, 300), # 0x43 commits ok
        # 0x42 is lost
    ]
    
    for e in events:
        monitor.process_event(e)
    
    # Advance time to timeout 0x42 (100 + 100 = 200, current ~300)
    monitor.check_timeouts(350)
    
    for log in monitor.history:
        print(log)
    monitor.history.clear()
    monitor.active_instances.clear()

    # --- Scenario 2: LR/SC Atomicity ---
    # Simplified: Trigger(LR).require(SC_Fail) IF Conflicting Write 
    # BUT current engine is Trigger->Obligation. 
    # Let's map "Conflicting Write" as an *Abort* condition for *Success*? No, that's inverted.
    # Let's try: Trigger(LR) -> Obligation(SC_Success) ... unless(ConflictingWrite)?
    # If "unless" happens, rule is Cancelled (meaning obligation dropped).
    # IF we want to enforce SC_Fail, we need a refined logic.
    # "If conflicting write, SC MUST fail" <=> "SC Success IS FORBIDDEN"
    # For now, let's implement the 'Safety Violation' test from the example:
    # Trigger: LR. 
    # Obligation: SC_Result (Success or Fail).
    # If we see Write in between, we conceptually change the requirement.
    # This requires stateful obligations or predicates.
    # For this prototype, I'll Skip C003 sophisticated logic and settle for:
    # "LR -> SC within 50 cycles" just to test binding on 'granule'
    
    r_lrsc = (
        Rule("Basic_LR_SC_Pair")
        .when(Signal("LR_executed", binds=["granule"]))
        .require(Signal("SC_executed", match_binds=["granule"]))
        .within(50)
    )
    monitor.add_rule(r_lrsc)
    
    print("\n--- Example 2: LR/SC Binding Check ---")
    events_lrsc = [
        Event("LR_executed", {"granule": 0x100}, 10),
        Event("LR_executed", {"granule": 0x200}, 12),
        Event("SC_executed", {"granule": 0x100}, 20), # Matches first
        Event("SC_executed", {"granule": 0x200}, 80), # Too late for second (12+50=62)
    ]
    
    for e in events_lrsc:
        monitor.process_event(e)
    monitor.check_timeouts(100)

    for log in monitor.history:
        print(log)

if __name__ == "__main__":
    run_demo()
