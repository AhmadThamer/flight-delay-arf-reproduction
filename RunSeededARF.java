import moa.classifiers.meta.AdaptiveRandomForest;
import moa.options.ClassOption;
import moa.tasks.EvaluatePrequentialCV;
import moa.tasks.MainTask;

/** Sets the forest seed through MOA's API, then runs an unchanged MOA task.
 * MOA 24.07 does not expose the ARF learner seed as a CLI option.
 * Usage: java -cp moa.jar RunSeededARF.java SEED "EvaluatePrequentialCV ..."
 */
public class RunSeededARF {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new IllegalArgumentException("Expected ARF seed and task string.");
        }
        int seed = Integer.parseInt(args[0]);
        EvaluatePrequentialCV task = (EvaluatePrequentialCV)
            ClassOption.cliStringToObject(args[1], MainTask.class, null);
        Object learner = task.learnerOption.getPreMaterializedObject();
        if (!(learner instanceof AdaptiveRandomForest)) {
            throw new IllegalArgumentException("Expected an AdaptiveRandomForest learner.");
        }
        ((AdaptiveRandomForest) learner).setRandomSeed(seed);
        System.out.println("ARF learner seed set through MOA API: " + seed);
        System.out.println("Task: " + args[1]);
        task.prepareForUse();
        Object result = task.doTask();
        System.out.println(result);
    }
}
