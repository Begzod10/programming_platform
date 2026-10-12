import { BookOpenCheck } from 'lucide-react';
import './UnmetLessons.css';

/** Lessons the team had not studied when the project was assigned (blueprint `requires`).
 *  Teacher: a heads-up that the team may struggle. Student: lessons worth finishing first. */
export default function UnmetLessons({ lessons, ru, audience }) {
    if (!Array.isArray(lessons) || lessons.length === 0) return null;
    const teacher = audience === 'teacher';
    const title = teacher
        ? (ru ? 'Команда ещё не прошла уроки для этого проекта' : "Jamoa bu loyiha uchun kerakli darslarni hali o'rganmagan")
        : (ru ? 'Полезно сначала пройти эти уроки' : "Avval shu darslarni tugatish foydali");
    return (
        <div className="unl" role="note">
            <p className="unl-title"><BookOpenCheck size={15} aria-hidden="true" /> {title}</p>
            <ul>{lessons.map(l => <li key={l}>{l}</li>)}</ul>
        </div>
    );
}
