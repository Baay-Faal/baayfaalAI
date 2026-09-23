"""
Point d'entrée principal pour l'agent local Baay-Faal.
Permet d'interagir en ligne de commande avec votre propre agent souverain.
"""

import argparse
import sys
from core.agent import BaayAgent
from voice.speaker import BaaySpeaker
from voice.listener import BaayListener


def main():
    parser = argparse.ArgumentParser(description="Baay-Faal : Agent IA Local Autonome & Souverain")
    parser.add_argument("goal", nargs="*", help="Objectif à réaliser (optionnel)")
    parser.add_argument("-v", "--voice", action="store_true", help="Active la synthèse vocale pour les réponses de l'agent")
    args = parser.parse_args()

    print("=" * 60)
    print("           BAAY-FAAL : AGENT IA LOCAL SOUVERAIN")
    print(f"  100% Hors-Ligne | Vanilla Python | Mode Vocal : {'ACTIVÉ 🔊' if args.voice else 'DÉSACTIVÉ 🔇'}")
    print("=" * 60)
    print("Tapez votre ordre (ou 'exit' pour quitter).\n")

    agent = BaayAgent()
    speaker = BaaySpeaker() if args.voice else None
    listener = BaayListener()

    # Si un ordre a été passé en argument de ligne de commande
    if args.goal:
        user_goal = " ".join(args.goal)
        answer = agent.run(user_goal)
        print("\n" + "=" * 40)
        print(f"[RÉPONSE FINALE]\n{answer}")
        print("=" * 40)
        if speaker:
            speaker.speak(answer, block=True)
        return

    # Mode interactif (REPL)
    while True:
        try:
            user_input = input("\n[VOUS] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("À bientôt. Jëf Jël !")
                if speaker:
                    speaker.speak("À bientôt. Jëf Jël !", block=True)
                break

            response = agent.run(user_input)
            print("\n" + "=" * 40)
            print(f"[BAAY-AGENT]\n{response}")
            print("=" * 40)

            if speaker:
                speaker.speak(response, block=False)

        except KeyboardInterrupt:
            print("\nArrêt demandé. À bientôt !")
            break


if __name__ == "__main__":
    main()
