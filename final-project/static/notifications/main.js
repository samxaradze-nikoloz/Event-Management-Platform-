document.addEventListener("DOMContentLoaded", () => {
    const toasts = document.querySelectorAll(".toast");

    toasts.forEach((toast, index) => {
        setTimeout(() => {
            toast.style.transition = "0.4s ease";
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-10px)";

            setTimeout(() => {
                toast.remove();
            }, 400);
        }, 4000 + (index * 300));
    });
});