import lxml.etree as ET
from tutorgym.shared import Action, ProblemState
from tutorgym.env_classes.fsm_tutor import StateMachineTutor, FiniteStateMachine
from tutorgym.env_classes.env_base import TutorEnvBase
from tutorgym.env_classes.CTAT.CTAT_problem_set import collect_CTAT_problem_sets
from tutorgym.env_classes.CTAT.brd_tools import parse_brd
from tutorgym.env_classes.CTAT.action_model import CTAT_ActionModel
from tutorgym.html_tools import HTML_Preprocessor
import json
from copy import copy
import re

# -----------------------------------------------------------------
# : Action Filters

def action_not_buggy(action):
    return action.get_annotation("action_type", None) != "Buggy Action"


template_pattern = re.compile("\%\(.*\)\%")
def action_not_template(action):
    inputs = action.sai[2]
    for k,v in inputs.items():
        if(template_pattern.search(str(k)) or
           template_pattern.search(str(v))):
            return False
    return True


# ------------------------------------------------------------------
# : CTAT_Tutor

class CTAT_Tutor(StateMachineTutor):
    def __init__(self, html_proc_config={"root_dir" : "./"},
                       action_filters=[action_not_buggy, action_not_template],
                    **kwargs):
        self.html_proc_config = html_proc_config
        self.html_proc = HTML_Preprocessor(**html_proc_config)
        self.action_filters = action_filters
        super().__init__(action_model=CTAT_ActionModel,**kwargs)

    def _satisfies_filters(self, action):
        for fltr in self.action_filters:
            # print("SKIPPING ACTION", action, f"Failed filter {fltr.__name__}")
            if(not fltr(action)):
                return False
        return True


    def create_fsm(self, start_state, **kwargs):
        fsm = FiniteStateMachine(
            start_state.copy(keep_annotations=True),
            self.action_model
        )

        # Start by indexing sets of edges by by their source node
        edge_dict = {}
        for node_unq_id, next_unq_id, action in self.edges:
            lst = edge_dict.get(node_unq_id, [])
            lst.append((next_unq_id, action))
            edge_dict[node_unq_id] = lst

        # Then expand edges in waves, one frontier at a time.
        #  A frontier is the set of unvisited nodes that were
        #  destinations of a previous wave's expanded edges. 
        frontier = set(["1"])
        covered = set()
        while len(frontier) > 0:
            new_frontier = set()
            for node_unq_id in frontier:
                if(node_unq_id in covered):
                    continue 

                node = fsm.nodes[node_unq_id]
                for next_unq_id, action in edge_dict[node_unq_id]:

                    
                    if(not self._satisfies_filters(action)):
                        continue
                    # if(action.get_annotation("action_type", None) == "Buggy Action"):
                    #     continue

                    next_state = fsm.add_edge(node['state'], action, 
                        force_unique_id=next_unq_id)

                    print(node_unq_id, next_unq_id, action.sai)

                    if(next_state.get_annotation("is_done", False)):
                        continue

                    new_frontier.add(next_unq_id)
                covered.add(node_unq_id)
            frontier = new_frontier

        return fsm

    def set_start_state(self, html_path, model_path, **kwargs):
        # Render the HTML converted the DOM to JSON and snap a picture
        configs = self.html_proc.process_htmls(
            [html_path],
            keep_alive=True
        )

        print(html_path)
        print(model_path)

        # Load the HTML converted to JSON
        with open(configs[0]['json_path']) as f:
            start_state = json.load(f)
            self.start_actions, self.edges, self.edge_groups = \
                parse_brd(model_path)

        # Apply any start state messages in the brd 
        for action in self.start_actions:
            start_state = self.apply(start_state, action, make_copy=False)
        start_state.action_history = []

        start_state.add_annotations({"is_start": True, "unique_id" : "1"})
        self.start_state = start_state

    def apply(self, state, action, **kwargs):
        return self.action_model.apply(state, action)





# parse_brd("AS_3_7_plus_4_7.brd")
# parse_brd("Mathtutor/6_01_HTML/FinalBRDs/Problem1.brd")

if __name__ == '__main__':

    tutor = CTAT_Tutor()
    problem_sets = collect_CTAT_problem_sets("../../envs/CTAT/Mathtutor/")
    for prob_set in problem_sets:
        for problem in prob_set:
            tutor.set_problem(**problem)






