import json
from os import path

from grackle.trainer.trainer import Trainer
from grackle.paramils import reparamils

SCENARIO = """
algo = %s
execdir = .
deterministic = 1
run_obj = runlength
overall_obj = mean
cutoff_time = %s
cutoff_length = max
tunerTimeout = %s
paramfile = params.txt
outdir = paramils-out
instance_file = instances.txt
test_instance_file = empty.tst
"""

class ParamilsTrainer(Trainer):
   
   def __init__(self, runner, config={}):
      Trainer.__init__(self, runner, config)
      self.default("restarts", False)

   def domains(self, params):
      raise NotImplementedError("Abstract method not implemented.")
   
   def improve(self, state, conf, insts):
      cwd = path.join("training", "iter-%03d-%s"%(state.it, self.confname(conf)))
      cwd = path.join(cwd, self.runner.config["nick"]) if "nick" in self.runner.config else cwd
      params = self.recall(conf)
      algo = "grackle-wrapper.py %s" % repr(json.dumps(self.runner.config))
      scenario = SCENARIO % (algo, state.trainer.runner.config["timeout"], state.trainer.config["timeout"])
      params = reparamils.launch(
         scenario, 
         domains=self.domains(params), 
         init=params, 
         insts=insts, 
         cwd=cwd, 
         timeout=self.trainlimit(len(insts)), 
         restarts=self.config["restarts"],
         cores=state.cores,
         logs=self.config["log"])
      params = self.runner.clean(params)
      return self.name(params) 

   def recall(self, conf):
      return self.runner.recall(conf)

   def name(self, params):
      return self.runner.name(params)

   def confname(self, conf):
      return conf

