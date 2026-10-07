jest.mock('lucide-react', () => new Proxy({ __esModule: true }, {
    get: (t, p) => (p in t || typeof p === 'symbol' ? t[p] : () => null),
}));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { FlashcardMode, ClozeMode } from '../views/student/dictionary/PracticeModes';

beforeEach(() => localStorage.setItem('lang', 'uz'));

describe('FlashcardMode', () => {
    test('a double tap on "Bilaman" answers only once', () => {
        const onAnswer = jest.fn();
        render(<FlashcardMode word={{ id: 1, word: 'array', context: 'Massiv' }} onAnswer={onAnswer} />);
        fireEvent.click(screen.getByRole('button', { name: /Aylantirish/ }));
        const known = screen.getByRole('button', { name: /Bilaman/ });
        fireEvent.click(known);
        fireEvent.click(known);
        expect(onAnswer).toHaveBeenCalledTimes(1);
        expect(onAnswer).toHaveBeenCalledWith({ grade: 2, was_correct: true });
    });
});

describe('ClozeMode', () => {
    test('blanks the word in the sentence', () => {
        render(<ClozeMode word={{ id: 1, word: 'array', context: 'An array holds items' }}
                          onAnswer={jest.fn()} request={jest.fn()} />);
        expect(screen.getByText('An _____ holds items')).toBeInTheDocument();
    });

    test('a sentence without the word falls back to the masked meaning instead of a free skip', () => {
        render(<ClozeMode word={{ id: 1, word: 'array', context: 'Massiv', context_masked: 'Massiv' }}
                          onAnswer={jest.fn()} request={jest.fn()} />);
        expect(screen.queryByRole('button', { name: /O'tkazib yuborish/ })).not.toBeInTheDocument();
        expect(screen.getByText('Massiv')).toBeInTheDocument();
    });

    test('with no text at all the card can be skipped, and a skip records nothing', () => {
        const onAnswer = jest.fn();
        render(<ClozeMode word={{ id: 1, word: 'array', context: '', context_masked: '' }}
                          onAnswer={onAnswer} request={jest.fn()} />);
        fireEvent.click(screen.getByRole('button', { name: /O'tkazib yuborish/ }));
        expect(onAnswer).toHaveBeenCalledWith({ skip: true, was_correct: true });
    });
});
