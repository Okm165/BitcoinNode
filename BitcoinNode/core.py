import utils.chainstate as CS
import utils.paths as PA
import chainparser as PR

cs = CS.ChainDb(PA.remotecs)

PR.parse(cs, progress=True)


