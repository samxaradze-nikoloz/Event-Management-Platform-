using System;
using System.Collections.Generic;
using Raylib_cs;



class SnakeGame
{
    const int Cols = 32;
    const int Rows = 24;
    const int CellSize = 24;
    const int ScreenWidth = Cols * CellSize;
    const int ScreenHeight = Rows * CellSize + 60; 

    const float InitialStepSeconds = 0.14f;
    const float MinStepSeconds = 0.06f;
    const float StepDecrement = 0.004f;

    enum Direction { Up, Down, Left, Right }
    enum GameState { Title, Playing, GameOver }

    static readonly Random Rng = new Random();

    static void Main()
    {
        Raylib.InitWindow(ScreenWidth, ScreenHeight, "Snake");
        Raylib.SetTargetFPS(60);

        var state = GameState.Title;
        List<(int X, int Y)> snake = null!;
        Direction direction = Direction.Up;
        Direction pendingDirection = Direction.Up;
        (int X, int Y) food = (0, 0);
        int score = 0;
        float stepSeconds = InitialStepSeconds;
        float timer = 0f;

        while (!Raylib.WindowShouldClose())
        {
            switch (state)
            {
                case GameState.Title:
                    if (Raylib.IsKeyPressed(KeyboardKey.Enter) || Raylib.IsKeyPressed(KeyboardKey.Space))
                    {
                        (snake, direction, pendingDirection, food, score, stepSeconds, timer) = NewGame();
                        state = GameState.Playing;
                    }
                    break;

                case GameState.Playing:
                    pendingDirection = ReadDirectionInput(direction, pendingDirection);

                    timer += Raylib.GetFrameTime();
                    if (timer >= stepSeconds)
                    {
                        timer -= stepSeconds;
                        direction = pendingDirection;

                        var head = snake[0];
                        var newHead = WrapPosition(MoveHead(head, direction));
                        bool ateFood = newHead == food;

                        if (SnakeCollides(snake, newHead, ateFood))
                        {
                            state = GameState.GameOver;
                            break;
                        }

                        snake.Insert(0, newHead);
                        if (ateFood)
                        {
                            score += 10;
                            food = SpawnFood(snake);
                            if (stepSeconds > MinStepSeconds) stepSeconds -= StepDecrement;
                        }
                        else
                        {
                            snake.RemoveAt(snake.Count - 1);
                        }
                    }
                    break;

                case GameState.GameOver:
                    if (Raylib.IsKeyPressed(KeyboardKey.Y) || Raylib.IsKeyPressed(KeyboardKey.Enter))
                    {
                        (snake, direction, pendingDirection, food, score, stepSeconds, timer) = NewGame();
                        state = GameState.Playing;
                    }
                    else if (Raylib.IsKeyPressed(KeyboardKey.N) || Raylib.IsKeyPressed(KeyboardKey.Escape))
                    {
                        Raylib.CloseWindow();
                        return;
                    }
                    break;
            }

            Raylib.BeginDrawing();
            Raylib.ClearBackground(new Color(18, 18, 24, 255));

            switch (state)
            {
                case GameState.Title:
                    DrawCentered("SNAKE", ScreenHeight / 2 - 60, 48, Color.Green);
                    DrawCentered("Press ENTER to start", ScreenHeight / 2, 22, Color.White);
                    DrawCentered("Arrow keys / WASD to move, Esc to quit", ScreenHeight / 2 + 32, 16, Color.Gray);
                    break;

                case GameState.Playing:
                    DrawBoard(snake, food);
                    DrawHud(score);
                    break;

                case GameState.GameOver:
                    DrawBoard(snake, food);
                    DrawHud(score);
                    Raylib.DrawRectangle(0, 0, ScreenWidth, ScreenHeight, new Color(0, 0, 0, 160));
                    DrawCentered("GAME OVER", ScreenHeight / 2 - 50, 44, Color.Red);
                    DrawCentered($"Score: {score}", ScreenHeight / 2, 24, Color.White);
                    DrawCentered("Play again? (Y/N)", ScreenHeight / 2 + 34, 20, Color.White);
                    break;
            }

            Raylib.EndDrawing();
        }

        Raylib.CloseWindow();
    }

    static (List<(int X, int Y)>, Direction, Direction, (int X, int Y), int, float, float) NewGame()
    {
        var snake = new List<(int X, int Y)>
        {
            (Cols / 2, Rows / 2),
            (Cols / 2, Rows / 2 + 1),
            (Cols / 2, Rows / 2 + 2),
        };
        var direction = Direction.Up;
        var food = SpawnFood(snake);
        return (snake, direction, direction, food, 0, InitialStepSeconds, 0f);
    }

    static Direction ReadDirectionInput(Direction current, Direction pending)
    {
        Direction? requested = null;
        if (Raylib.IsKeyPressed(KeyboardKey.Up) || Raylib.IsKeyPressed(KeyboardKey.W)) requested = Direction.Up;
        else if (Raylib.IsKeyPressed(KeyboardKey.Down) || Raylib.IsKeyPressed(KeyboardKey.S)) requested = Direction.Down;
        else if (Raylib.IsKeyPressed(KeyboardKey.Left) || Raylib.IsKeyPressed(KeyboardKey.A)) requested = Direction.Left;
        else if (Raylib.IsKeyPressed(KeyboardKey.Right) || Raylib.IsKeyPressed(KeyboardKey.D)) requested = Direction.Right;

        if (requested.HasValue && !IsOpposite(current, requested.Value))
            return requested.Value;

        return pending;
    }

    static bool IsOpposite(Direction a, Direction b) =>
        (a == Direction.Up && b == Direction.Down) ||
        (a == Direction.Down && b == Direction.Up) ||
        (a == Direction.Left && b == Direction.Right) ||
        (a == Direction.Right && b == Direction.Left);

    static (int X, int Y) MoveHead((int X, int Y) head, Direction dir) => dir switch
    {
        Direction.Up => (head.X, head.Y - 1),
        Direction.Down => (head.X, head.Y + 1),
        Direction.Left => (head.X - 1, head.Y),
        Direction.Right => (head.X + 1, head.Y),
        _ => head
    };

    static (int X, int Y) WrapPosition((int X, int Y) pos)
    {
        int x = pos.X, y = pos.Y;
        if (x < 0) x = Cols - 1;
        if (x >= Cols) x = 0;
        if (y < 0) y = Rows - 1;
        if (y >= Rows) y = 0;
        return (x, y);
    }

    static bool SnakeCollides(List<(int X, int Y)> snake, (int X, int Y) newHead, bool willGrow)
    {
        int cellsToCheck = willGrow ? snake.Count : snake.Count - 1;
        for (int i = 0; i < cellsToCheck; i++)
            if (snake[i] == newHead) return true;
        return false;
    }

    static (int X, int Y) SpawnFood(List<(int X, int Y)> snake)
    {
        var occupied = new HashSet<(int, int)>(snake);
        (int X, int Y) food;
        do
        {
            food = (Rng.Next(0, Cols), Rng.Next(0, Rows));
        } while (occupied.Contains(food));
        return food;
    }

    static void DrawBoard(List<(int X, int Y)> snake, (int X, int Y) food)
    {
        int boardTop = 60;

        
        Raylib.DrawRectangle(0, boardTop, ScreenWidth, ScreenHeight - boardTop, new Color(28, 28, 36, 255));

        Raylib.DrawRectangle(food.X * CellSize, boardTop + food.Y * CellSize, CellSize, CellSize, Color.Red);

        
        for (int i = 0; i < snake.Count; i++)
        {
            var seg = snake[i];
            var color = i == 0 ? Color.Lime : Color.Green;
            Raylib.DrawRectangle(seg.X * CellSize + 1, boardTop + seg.Y * CellSize + 1, CellSize - 2, CellSize - 2, color);
        }
    }

    static void DrawHud(int score)
    {
        Raylib.DrawText($"Score: {score}", 10, 16, 24, Color.White);
        Raylib.DrawText("Esc to quit", ScreenWidth - 130, 16, 18, Color.Gray);
    }

    static void DrawCentered(string text, int y, int fontSize, Color color)
    {
        int width = Raylib.MeasureText(text, fontSize);
        Raylib.DrawText(text, (ScreenWidth - width) / 2, y, fontSize, color);
    }
}