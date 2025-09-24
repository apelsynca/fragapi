import { Link } from "@tanstack/react-router";
import { Button } from "../ui/button";

export const HeroLogin: React.FC<{ isLoggedIn: boolean }> = ({
  isLoggedIn,
}) => {
  if (isLoggedIn) {
    return (
      <Link to="/home">
        <Button>Войти</Button>
      </Link>
    );
  }

  return (
    <a href={`https://t.me/${import.meta.env.VITE_BOT_USERNAME}?start=login`}>
      <Button>Войти через Бота</Button>
    </a>
  );
};
