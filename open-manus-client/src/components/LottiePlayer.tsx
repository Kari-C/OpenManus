import Lottie from "react-lottie-player";

interface LottiePlayerProps {
    src: string;
    autoplay?: boolean;
    width?: number | string;
    height?: number | string;
    loop?: boolean;
    speed?: number;
    backgroundColor?: string;
}

export default function LottiePlayer({
    src,
    width,
    height,
    speed = 1,
    loop = false,
    autoplay = true,
    backgroundColor
}: LottiePlayerProps) {
    return (
        <Lottie
            play={autoplay}
            loop={loop}
            speed={speed}
            path={`./${src}.json`}
            style={{
                width: width,
                height: height,
                backgroundColor: backgroundColor
            }}
        />
    );
}
