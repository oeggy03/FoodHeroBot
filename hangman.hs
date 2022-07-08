guesses_in_string :: String -> String -> Bool
--
-- Checks if any character in the guesses string is present in the word string
-- Returns True if there is a matching character, False otherwise
--
-- guesses_in_string word guessed_letters
--
guesses_in_string [] [] = False
guesses_in_string x [] = False
guesses_in_string [] y = False
guesses_in_string (x:xs) (y:ys)
  | x == y             = True
  | otherwise          = (guesses_in_string xs (y:ys)) || (guesses_in_string (x:xs) ys)


letter_in_string :: String -> String -> Bool
--
-- Checks if the guessed letter is present in the word string
-- Returns True if there is a matching character, False otherwise
--
-- letter_in_string word letter
--
letter_in_string [] y = False
letter_in_string (x:xs) (y:ys)
  | x == y             = True
  | otherwise          = (guesses_in_string xs (y:ys))


guessed_word :: String -> String -> String
--
-- Takes the string of guessed letters and the word
-- Returns the word guessed so far, with characters not yet guessed
-- being replaced with "_"
--
-- guessed_word word guessed_letters
--
guessed_word "" y = ""
guessed_word (x:xs) y
  | guesses_in_string [x] y = x : guessed_word xs y
  | otherwise             = '_' : guessed_word xs y

incorrect_guesses :: String -> String -> String
--
-- Takes the string of guessed letters and the word
-- Returns the characters guessed not present in the word
--
-- incorrect_guesses word guessed_letters
--
incorrect_guesses x "" = ""
incorrect_guesses x (y:ys)
  | not (guesses_in_string x (y:ys)) = y : ' ' : incorrect_guesses x ys
  | otherwise                        = ' ' : incorrect_guesses x ys

play_hangman :: String -> String -> Integer -> IO()
play_hangman word guesses lives = do
  if (guessed_word word guesses) == word
    then putStrLn "pog u won"
  else if lives == 0
    then putStrLn "xd git gud u died"
  else
    do putStrLn ("u have " ++ show lives ++ " live(s) left dont die")
       putStrLn ("this is your word now:  " ++ guessed_word word guesses)
       putStrLn ("u got these guesses wrong smh : " ++ incorrect_guesses word guesses)
       putStrLn ("time for your next guess idiot: ")
       next_letter <- getLine
       putStrLn ("---------------------------------")
       let new_guesses = next_letter ++ guesses
       -- New guess string to show another guess has been added
       if guessed_word word guesses /= guessed_word word new_guesses
         -- If guessing the new letter changed what's been guessed, then
         -- a new letter is found and no lives are subtracted
         -- otherwise 1 life is subtracted
         then play_hangman word new_guesses lives
       else
         -- idk how to fix this to make it yell at your
         -- for guessing a thing you guessed before
         -- vvvv
         --
         -- if letter_in_string guesses next_letter
         --    then putStrLn "bruh you already guessed that"
         --    else return ()
         play_hangman word new_guesses (lives-1)

main :: IO()
main = do
  putStrLn "gimme a word bish"
  word <- getLine
  putStr "\ESC[2J" --Clear terminal, idk if this works for you too
  let guesses = ""
  let lives = 6
  play_hangman word guesses lives
