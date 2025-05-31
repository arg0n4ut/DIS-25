package hamburg.dbis.utils;

import java.util.HashSet;
import java.util.Random;

public class RandomHashSet<T> extends HashSet<T> {

    public T getRandomElement() {
        if (this.size() <= 0) {
            return null;
        }

        int size = this.size();
        int item = new Random().nextInt(size);
        int i = 0;
        for (T element : this) {
            if (i == item) {
                return element;
            }
            i++;
        }
        return null;
    }
}
