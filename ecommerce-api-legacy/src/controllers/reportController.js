function reportController({ courseModel, enrollmentModel, userModel, paymentModel }) {
    return {
        async buildFinancialReport() {
            const courses = await courseModel.findAll();
            if (courses.length === 0) return [];

            const courseIds = courses.map((c) => c.id);
            const enrollments = await enrollmentModel.findByCourseIds(courseIds);

            const enrollmentIds = enrollments.map((e) => e.id);
            const userIds = [...new Set(enrollments.map((e) => e.user_id))];

            const [users, payments] = await Promise.all([
                userModel.findByIds(userIds),
                paymentModel.findByEnrollmentIds(enrollmentIds),
            ]);

            const usersById = new Map(users.map((u) => [u.id, u]));
            const paymentsByEnrollmentId = new Map(payments.map((p) => [p.enrollment_id, p]));
            const enrollmentsByCourseId = new Map();
            for (const enrollment of enrollments) {
                const list = enrollmentsByCourseId.get(enrollment.course_id) || [];
                list.push(enrollment);
                enrollmentsByCourseId.set(enrollment.course_id, list);
            }

            return courses.map((course) => {
                const courseEnrollments = enrollmentsByCourseId.get(course.id) || [];
                let revenue = 0;
                const students = courseEnrollments.map((enrollment) => {
                    const user = usersById.get(enrollment.user_id);
                    const payment = paymentsByEnrollmentId.get(enrollment.id);
                    if (payment && payment.status === 'PAID') {
                        revenue += payment.amount;
                    }
                    return {
                        student: user ? user.name : 'Unknown',
                        paid: payment ? payment.amount : 0,
                    };
                });
                return { course: course.title, revenue, students };
            });
        },
    };
}

module.exports = reportController;
